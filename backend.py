import os
import faiss
from dotenv import load_dotenv
import numpy as np
from langchain.chains import RetrievalQA
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.document_loaders import PyPDFDirectoryLoader
from langchain.schema import Document

# Importing API keys
load_dotenv()
HUGGINGFACE_TOKEN = os.getenv("HUGGINGFACE_TOKEN")

# Define the data directory where your PDFs are stored
DATA_DIR = "C:/csusb_fall2024_cse6550_team4/Volumes"
INDEX_FILE = "faiss_index.bin"

# Function to load PDFs using PyPDF Directory Loader
def load_pdfs(data_dir):
    loader = PyPDFDirectoryLoader(data_dir)
    documents = loader.load()
    for doc in documents:
        if "paper1.pdf" in doc.metadata["source"]:
            doc.metadata["source"] = "https://dl.acm.org/doi/10.1145/3597503.3649398"
        elif "paper2.pdf" in doc.metadata["source"]:
            doc.metadata["source"] = "https://dl.acm.org/doi/10.1145/3597503.3649399"
    return documents

# Function to split documents into smaller chunks
def split_documents(documents):
    from langchain.text_splitter import RecursiveCharacterTextSplitter
    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    split_docs = []
    for doc in documents:
        chunks = splitter.split_text(doc.page_content)
        for chunk in chunks:
            split_docs.append(Document(page_content=chunk, metadata=doc.metadata))
    return split_docs

# Initialize embeddings
def initialize_embeddings():
    return HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

# Create FAISS index
def create_faiss_index(data_dir, index_file):
    documents = load_pdfs(data_dir)
    split_docs = split_documents(documents)
    embeddings = initialize_embeddings()
    vector_store = FAISS.from_documents(split_docs, embeddings)
    vector_store.save_local(index_file)
    return vector_store

# Load FAISS vector store
def load_faiss_vector_store(index_file, embeddings):
    if os.path.exists(index_file):
        return FAISS.load_local(index_file, embeddings, allow_dangerous_deserialization=True)
    return None

# Load fine-tuned model for chatbot
from transformers import GPTNeoForCausalLM, GPT2Tokenizer
def load_fine_tuned_model():
    model = GPTNeoForCausalLM.from_pretrained("./fine_tuned_model")
    tokenizer = GPT2Tokenizer.from_pretrained("./fine_tuned_model")
    return model, tokenizer

# Initialize the RetrievalQA pipeline with the fine-tuned model
def initialize_qa_pipeline(vector_store):
    model, tokenizer = load_fine_tuned_model()

    # Set up HuggingFaceHub to load the fine-tuned model
    from langchain.llms import HuggingFaceHub
    llm = HuggingFaceHub(
        repo_id="./fine_tuned_model", 
        huggingfacehub_api_token=os.getenv("HUGGINGFACE_TOKEN")
    )

    retriever = vector_store.as_retriever()
    retriever.search_kwargs = {"k": 1}

    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        retriever=retriever,
        return_source_documents=True,
        chain_type="stuff"
    )
    
    return qa_chain


