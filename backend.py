import os
import faiss
from dotenv import load_dotenv
import numpy as np
from langchain.chains import RetrievalQA
from langchain_community.vectorstores import FAISS  # Updated import for FAISS
from langchain_huggingface import HuggingFaceEmbeddings  # Updated import for HuggingFaceEmbeddings
from langchain_community.document_loaders import PyPDFDirectoryLoader  # Updated import for PDF loader
from langchain_community.llms import HuggingFaceHub  # Updated import for HuggingFaceHub
from langchain.schema import Document  # Import Document class for document structure

# Importing API keys
load_dotenv()
HUGGINGFACE_API_KEY = os.getenv("HUGGINGFACE_API_KEY")

# Define the data directory where your PDFs are stored
DATA_DIR = "C:\\csusb_fall2024_cse6550_team4\\Volumes"
INDEX_FILE = "faiss_index.bin"

# Function to load PDFs using PyPDF Directory Loader
def load_pdfs(data_dir):
    loader = PyPDFDirectoryLoader(data_dir)
    documents = loader.load()  # This will extract text from all PDFs in the directory
    # Add a source metadata for each document, here you might use the file path or URL
    for doc in documents:
        if "paper1.pdf" in doc.metadata["source"]:
            doc.metadata["source"] = "https://dl.acm.org/doi/10.1145/3597503.3649398"
        elif "paper2.pdf" in doc.metadata["source"]:
            doc.metadata["source"] = "https://dl.acm.org/doi/10.1145/3597503.3649399"
    
    return documents

# Function to split documents into smaller chunks using Recursive Text Splitter
def split_documents(documents):
    from langchain.text_splitter import RecursiveCharacterTextSplitter
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,  # Max size for each chunk
        chunk_overlap=200  # Overlap between chunks to preserve context
    )
    
    split_docs = []
    for doc in documents:
        chunks = splitter.split_text(doc.page_content)
        # Convert each chunk into a Document object
        for chunk in chunks:
            split_docs.append(Document(page_content=chunk, metadata=doc.metadata))
    
    return split_docs

# Initialize the HuggingFace embeddings model
def initialize_embeddings():
    return HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

# Function to create the FAISS index and save it
def create_faiss_index(data_dir, index_file):
    # Load PDFs and extract text
    documents = load_pdfs(data_dir)
    
    # Split the documents into smaller chunks
    split_docs = split_documents(documents)
    
    # Initialize embeddings
    embeddings = initialize_embeddings()

    # Initialize FAISS vector store from documents and embeddings
    vector_store = FAISS.from_documents(split_docs, embeddings)
    
    # Save the FAISS index to a file
    vector_store.save_local(index_file)
    
    return vector_store  # Return the vector store with .as_retriever method

# Load FAISS vector store from the saved index
def load_faiss_vector_store(index_file, embeddings):
    if os.path.exists(index_file):
        # Load FAISS vector store from disk
        return FAISS.load_local(index_file, embeddings, allow_dangerous_deserialization=True)
    else:
        return None

# Initialize the RetrievalQA pipeline using Langchain
from langchain.prompts import PromptTemplate
from langchain.chains import RetrievalQA

# Initialize the RetrievalQA pipeline using Langchain
def initialize_qa_pipeline(vector_store):

    #Adding prompt
    prompt_template = """{context}

    Question: {question}

    Answer:"""

    # Initialize the HuggingFaceHub model for response generation
    llm = HuggingFaceHub(repo_id="EleutherAI/gpt-neo-125M", huggingfacehub_api_token=os.getenv("HUGGINGFACE_API_KEY"))
    
    # Create the retriever and limit it to return only 1 document per query
    retriever = vector_store.as_retriever()
    retriever.search_kwargs = {"k": 1}  # Only retrieve 1 document per query
    
    # Create the RetrievalQA chain using from_chain_type
    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        retriever=retriever,
        return_source_documents=True,  # This ensures that citations are returned
        chain_type="stuff"  # You can also use "map_reduce" or other chain types based on your needs
    )
    
    return qa_chain

# Function to get chatbot response
def get_chatbot_response(qa_pipeline, user_input):
    # Use the QA pipeline to generate a response and retrieve source documents
    response = qa_pipeline({"query": user_input})
    
    # Extract the chatbot response
    bot_response = response['result']
    
    # Extract citation sources and format them as clickable URLs
    sources = response['source_documents']
    
     # Dynamically create Markdown links for each source, using the title as the link text
    citations = ', '.join(
        [f"[{doc.metadata.get('source')}]({doc.metadata.get('source')})" for doc in sources if doc.metadata.get('source')])
   
    
    return bot_response, citations

