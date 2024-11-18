import os
import pickle
import uuid
from dotenv import load_dotenv
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.schema import Document
from langchain_core.prompts import PromptTemplate
#from langchain_mistralai import MistralAIEmbeddings
from langchain_mistralai.chat_models import ChatMistralAI
#from langchain_cohere import ChatCohere
from langchain_milvus import Milvus
from langchain_community.document_loaders import WebBaseLoader, RecursiveUrlLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain.chains import create_retrieval_chain
from langchain_huggingface import HuggingFaceEmbeddings
from pymilvus import connections, utility
from requests.exceptions import HTTPError
from httpx import HTTPStatusError
from langchain_community.document_loaders import PyPDFDirectoryLoader
from roman import toRoman
from PyPDF2 import PdfReader

load_dotenv()
MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")

MILVUS_URI = "./milvus/milvus_vector.db"
MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
data_dir = "./volumes"
CACHE_FILE = "./document_cache.pkl"
from langchain.schema import BaseRetriever
import numpy as np
from pydantic import Field
from typing import List, Any

class ScoreThresholdRetriever(BaseRetriever):
    """
    A retriever that retrieves relevant documents based on similarity scores from a vector store.

    Attributes:
        vector_store (Any): The vector store for similarity search.
        score_threshold (float): Minimum normalized score to consider a document relevant.
        k (int): Number of documents to retrieve.

    """

    vector_store: Any = Field(..., description="Vector store for similarity search")
    score_threshold: float = Field(default=0.1, description="Minimum score threshold for a document to be considered relevant")
    k: int = Field(default=1, description="Number of documents to retrieve")

    def get_relevant_documents(self, query:str) -> List[Any]:
        """
        Get relevant documents based on the query

        Args:
            query (str): The query string

        Returns:
            List[Document]: The list of relevant documents
        """
        try:
            docs_and_scores = self.vector_store.similarity_search_with_score(query, k=self.k)
        except Exception:
            return []

        if not docs_and_scores:
        # If no documents are found, return an empty list or a default message
            return []

        # Initialize variables for tracking the most relevant document
        highest_score = -1
        most_relevant_document = None

        for doc, score in docs_and_scores:
            normalized_score = self._normalize_score(score)

            # Check if the document is relevant and has a higher score than the current highest score
            if normalized_score >= self.score_threshold and normalized_score > highest_score:
                highest_score = normalized_score
                most_relevant_document = doc
                
                most_relevant_document.metadata["score"] = normalized_score
                most_relevant_document.metadata["title"] = doc.metadata.get("title", "Untitled")
                most_relevant_document.metadata["source"] = doc.metadata.get("source", "Unknown")

        return [most_relevant_document] if most_relevant_document else []
    
    @staticmethod
    def _normalize_score(score):
        """
        Normalize the score to a value between 0 and 1

        Args:
            score (float): The score to be normalized

        Returns:
            float: The normalized score
        """
        # Assuming Milvus L2 distance, adjust based on your distance metric
        max_distance = np.sqrt(2)
        normalized = 1 - (score / max_distance)
        return max(0, min(1, normalized))

def get_embedding_function():
    """
    returns embedding function for the model

    Returns:
        embedding function
    """
    embedding_function = HuggingFaceEmbeddings(model_name=MODEL_NAME)
    return embedding_function

def load_pdfs_in_batches(data_dir, batch_size=20):
    """
    Load PDFs in batches to avoid memory overload.
    If a cache file exists, load previously processed files from it and only process new files.
    """
    documents = []
    file_list = [f for f in os.listdir(data_dir) if f.endswith(".pdf")]
    processed_files = {}

    # Load the cache if it exists
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, "rb") as cache_file:
            processed_files = pickle.load(cache_file)
        print("Loaded processed files from cache.")

    new_files = [f for f in file_list if f not in processed_files]

    # Process new files in batches
    for i in range(0, len(new_files), batch_size):
        batch_files = new_files[i:i + batch_size]
        
        for filename in batch_files:
            pdf_path = os.path.join(data_dir, filename)
            reader = PdfReader(pdf_path)

            for page_num, page in enumerate(reader.pages):
                text = page.extract_text() or ""
                unique_id = str(uuid.uuid4())
                documents.append(Document(page_content=text, metadata={"source": pdf_path, "page": page_num + 1, "id": unique_id}))

            # Mark the file as processed
            processed_files[filename] = True

        # Save the updated cache after processing each batch
        with open(CACHE_FILE, "wb") as cache_file:
            pickle.dump(processed_files, cache_file)
        print(f"Processed and cached batch {i // batch_size + 1}/{len(new_files) // batch_size + 1}")

        yield documents
        documents = []  # Clear batch after yield

    if not new_files:
        print("No new files to process.")


def query_rag(query):
    """
    Entry point for the RAG model to generate an answer to a given query.

    Args:
        query (str): The query string for which an answer is to be generated.
    
    Returns:
        str: The formatted answer with a unique source link (if available).
    """
    # Define the model
    model = ChatMistralAI(model='open-mistral-7b', api_key=MISTRAL_API_KEY, temperature=0.2)
    print("Model Loaded")

    prompt = create_prompt()

    # Load the vector store and create the retriever
    vector_store = load_exisiting_db(uri=MILVUS_URI)
    retriever = ScoreThresholdRetriever(vector_store=vector_store, score_threshold=0.2, k=3)  # Adjust k as needed
    
    try:
        # Set up document and retrieval chains
        document_chain = create_stuff_documents_chain(model, prompt)
        print("Document Chain Created")

        retrieval_chain = create_retrieval_chain(retriever, document_chain)
        print("Retrieval Chain Created")

        # Get relevant documents
        relevant_docs = retriever.get_relevant_documents(query)
        print(f"Relevant Documents: {relevant_docs}")
        
        # Generate response
        response = retrieval_chain.invoke({"input": query})
        response_text = response.get("answer", "No answer found.")

        # Collect unique links
        unique_links = set()
        for doc in relevant_docs:
            metadata = doc.metadata if hasattr(doc, "metadata") else {}
            source = metadata.get("source", "Unknown").split("/")[-1]
            page = metadata.get("page", "Unknown")

            # Ensure page is an integer
            try:
                page = int(page)
            except ValueError:
                page = 1  # Default to page 1 if invalid

            # Create a unique link
            if source != "Unknown":
                link = f'<a href="/team4/?view=pdf&file={data_dir}/{source}&page={page}" target="_blank">[more_info]</a>'
                unique_links.add(link)  # Adds only if link is unique

        # Append source links to response text
        if unique_links:
            response_text += f"\n\nSource: {''.join(unique_links)}"

        return response_text

    except HTTPStatusError as e:
        print(f"HTTPStatusError: {e}")
        if e.response.status_code == 429:
            return "I am currently experiencing high traffic. Please try again later."
        return f"HTTPStatusError: {e}"



def create_prompt():
    """
    Create a prompt template for the RAG model

    Returns:
        PromptTemplate: The prompt template for the RAG model
    """
    # Define the prompt template
    PROMPT_TEMPLATE = """
    Human: You are an AI assistant, and provides answers to questions by using fact based and statistical information when possible.
    Use the following pieces of information to provide a concise answer to the question enclosed in <question> tags.
    Only use the information provided in the <context> tags.
    If you don't know the answer, just say that you don't know, don't try to make up an answer.
    <context>
    {context}
    </context>

    <question>
    {input}
    </question>

    The response should be specific and use statistics or numbers when possible.

    Assistant:"""

    # Create a PromptTemplate instance with the defined template and input variables
    prompt = PromptTemplate(
        template=PROMPT_TEMPLATE, input_variables=["context", "question"]
    )
    print("Prompt Created")

    return prompt


def initialize_milvus(uri: str=MILVUS_URI):
    """
    Initialize the vector store for the RAG model

    Args:
        uri (str, optional): Path to the local milvus db. Defaults to MILVUS_URI.

    Returns:
        vector_store: The vector store created
    """
    embeddings = get_embedding_function()
    vector_store = None

    for documents in load_pdfs_in_batches(data_dir):
        docs = split_documents(documents)
        if vector_store is None:
            vector_store = create_vector_store(docs, embeddings, uri)
        else:
            vector_store.add_documents(docs)

    print("Vector store initialization complete.")
    return vector_store


def load_documents_from_web():
    """
    Load the documents from the web and store the page contents

    Returns:
        list: The documents loaded from the web
    """
    # loader = RecursiveUrlLoader(
    #     url=CORPUS_SOURCE,
    #     prevent_outside=True,
    #     base_url=CORPUS_SOURCE
    # )
    documents = []
    for url in CORPUS_SOURCE:
        loader = WebBaseLoader(url)
        try:
            loaded_docs = loader.load()
            documents.extend(loaded_docs)  # Add loaded documents to the main list
            print(f"Documents loaded from {url}")
        except Exception as e:
            print(f"Failed to load documents from {url}: {e}")

    # loader = WebBaseLoader(CORPUS_SOURCE)
    # documents = loader.load()
    
    return documents

def split_documents(documents):
    """
    Split the documents into chunks

    Args:
        documents (list): The documents to split

    Returns:
        list: list of chunks of documents
    """
    # Create a text splitter to split the documents into chunks
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=2000,  # Split the text into chunks of 1000 characters
        chunk_overlap=200,  # Overlap the chunks by 300 characters
        is_separator_regex=False,  # Don't split on regex
    )
    # Split the documents into chunks
    docs = text_splitter.split_documents(documents)
    return docs


def create_vector_store(docs, embeddings, uri):
    """
    This function initializes a vector store using the provided documents and embeddings.
    It connects to a local Milvus database specified by the URI. If a collection named "IT_support" already exists,
    it loads the existing vector store; otherwise, it creates a new vector store and drops any existing one.

    Args:
        docs (list): A list of documents to be stored in the vector store.
        embeddings : A function or model that generates embeddings for the documents.
        uri (str): Path to the local milvus db

    Returns:
        vector_store: The vector store created
    """
    # Create the directory if it does not exist
    head = os.path.split(uri)
    os.makedirs(head[0], exist_ok=True)

    # Connect to the Milvus database
    connections.connect("default",uri=uri)

    # Check if the collection already exists
    if utility.has_collection("research_paper_chatbot"):
        print("Collection already exists. Loading existing Vector Store.")
        # loading the existing vector store
        vector_store = Milvus(
            collection_name="research_paper_chatbot",
            embedding_function=get_embedding_function(),
            connection_args={"uri": uri}
        )
    else:
        # Create a new vector store and drop any existing one
        vector_store = Milvus.from_documents(
            documents=docs,
            embedding=embeddings,
            collection_name="research_paper_chatbot",
            connection_args={"uri": uri},
            drop_old=True,
        )
        print("Vector Store Created")
    return vector_store


def load_exisiting_db(uri=MILVUS_URI):
    """
    Load an existing vector store from the local Milvus database specified by the URI.

    Args:
        uri (str, optional): Path to the local milvus db. Defaults to MILVUS_URI.

    Returns:
        vector_store: The vector store created
    """
    # Load an existing vector store
    vector_store = Milvus(
        collection_name="research_paper_chatbot",
        embedding_function = get_embedding_function(),
        connection_args={"uri": uri},
    )
    print("Vector Store Loaded")
    return vector_store

def get_answer_with_source(response):
    """
    Extract the answer and relevant source information from the response.
    This function processes the response from the RAG chain, extracting the answer
    and up to 5 source references (page numbers) from the context documents.

    Args:
        response (dict): The response dictionary from the RAG chain, containing 'answer' and 'context' keys.
    Returns:
        str: A formatted string containing the answer followed by source information.
    """
    # Extract the answer
    answer = response.get('answer', 'No answer found.')

    # Initialize source formatting
    sources = []
    context = response.get('context', '')

    if context:
        # Context might include multiple sources; parse these
        # For example, context could be a list of documents or metadata
        for idx, doc in enumerate(context.split(';')[:5], start=1):  # Limit to 5 sources
            source_info = f"[Source {idx}]({doc.strip()})"  # Customize as per your metadata structure
            sources.append(source_info)

    # Combine the answer with sources
    sources_info = " ".join(sources)
    formatted_response = f"{answer}\n\nSources: {sources_info}" if sources else answer

    return formatted_response


if __name__ == '__main__':
    pass