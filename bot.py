
# Web crawling function to load documents
CORPUS_SOURCE = 'https://dl.acm.org/doi/proceedings/10.1145/3597503'
import os
import faiss
from dotenv import load_dotenv
from langchain.chains import RetrievalQA
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.document_loaders import WebBaseLoader
from transformers import GPTNeoForCausalLM, GPT2Tokenizer
from pymilvus import connections, utility
from langchain.schema import Document

# Load environment variables from .env file
load_dotenv()

def load_documents_from_web():
    loader = WebBaseLoader(CORPUS_SOURCE)
    documents = loader.load()
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
def create_faiss_index(index_file):
    documents = load_documents_from_web()
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

# Initialize GPT-Neo model (not fine-tuned, pre-trained)
def load_gpt_neo_model():
    model = GPTNeoForCausalLM.from_pretrained("EleutherAI/gpt-neo-125M")
    tokenizer = GPT2Tokenizer.from_pretrained("EleutherAI/gpt-neo-125M")
    return model, tokenizer

# Initialize the RetrievalQA pipeline
def initialize_qa_pipeline(vector_store):
    retriever = vector_store.as_retriever()
    retriever.search_kwargs = {"k": 1}
    
    # Load the pre-trained GPT-Neo model and tokenizer
    model, tokenizer = load_gpt_neo_model()

    qa_chain = RetrievalQA.from_chain_type(
        llm=model,
        retriever=retriever,
        return_source_documents=True,
        chain_type="stuff"
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
    citations = ', '.join(
        [f"[{doc.metadata.get('source')}]({doc.metadata.get('source')})" for doc in sources if doc.metadata.get('source')]
    )
    
    return bot_response, citations

# Main function to initialize everything and process user queries
def main():
    embeddings = initialize_embeddings()

    # Check if FAISS index exists, if not, create it
    if not os.path.exists("faiss_index.bin"):
        vector_store = create_faiss_index("faiss_index.bin")
    else:
        vector_store = load_faiss_vector_store("faiss_index.bin", embeddings)

    qa_pipeline = initialize_qa_pipeline(vector_store)
    
    # Example of handling user input
    while True:
        user_input = input("Ask your question: ")
        if user_input.lower() == "exit":
            break
        response, citations = get_chatbot_response(qa_pipeline, user_input)
        print(f"Response: {response}")
        if citations:
            print(f"References: {citations}")

if __name__ == "__main__":
    main()
