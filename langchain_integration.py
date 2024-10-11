# langchain_integration.py
import os
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.retrievers import BM25Retriever
from langchain.retrievers import EnsembleRetriever
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFDirectoryLoader
from transformers import pipeline  # Importing Hugging Face's pipeline for text generation

# Load the text generation model
chatbot = pipeline('text-generation', model='EleutherAI/gpt-neo-125M')

EMBEDDING_MODEL_NAME = "Alibaba-NLP/gte-large-en-v1.5"  # Embedding model
model_kwargs = {'trust_remote_code': True}
EMBEDDING_FUNCTION = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL_NAME, model_kwargs=model_kwargs)

class LangChainChatbot:
    def __init__(self, document_path, persist_directory='faiss_index', collection_name='my_collection'):
        # Load documents
        self.documents = self.load_documents_from_directory(document_path)
        self.vector_store = self.load_or_create_faiss_vector_store(self.documents, collection_name, persist_directory)

    def load_documents_from_directory(self, document_path: str, chunk_size: int = 2048, chunk_overlap: int = 200):
        print(f"Loading documents from {document_path}...\n")
        documents = PyPDFDirectoryLoader(document_path).load_and_split()
        text_splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
        return text_splitter.split_documents(documents)

    def load_or_create_faiss_vector_store(self, documents, collection_name, persist_directory):
        index_path = os.path.join(persist_directory, f'{collection_name}_faiss_index')
        if os.path.exists(index_path):
            print(f"Loading existing FAISS vector store from {index_path}...\n")
            faiss_store = FAISS.load_local(index_path, embeddings=EMBEDDING_FUNCTION, allow_dangerous_deserialization=True)
        else:
            print(f"Creating new FAISS vector store in {index_path}...\n")
            faiss_store = FAISS.from_documents(documents, embedding=EMBEDDING_FUNCTION)
            faiss_store.save_local(index_path)
        return faiss_store

    def get_hybrid_retriever(self, documents, vector_store, k=5):
        bm25_retriever = BM25Retriever.from_documents(documents, search_kwargs={'k': k})
        vector_retriever = vector_store.as_retriever(search_kwargs={'k': k})
        fusion_retriever = EnsembleRetriever(
            retrievers=[bm25_retriever, vector_retriever],
            weights=[0.6, 0.4]
        )
        return fusion_retriever

    def get_response(self, user_input):
        # Use the Hugging Face model for generating a response
        response = chatbot(user_input, max_length=100, num_return_sequences=1)
        return response[0]['generated_text']
