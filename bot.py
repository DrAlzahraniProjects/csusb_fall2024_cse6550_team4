import os
import pickle
import uuid
from dotenv import load_dotenv
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.schema import Document
from langchain_core.prompts import PromptTemplate
from langchain_mistralai.chat_models import ChatMistralAI
from langchain_milvus import Milvus
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain.chains import create_retrieval_chain
from langchain_huggingface import HuggingFaceEmbeddings
from pymilvus import connections, utility
from httpx import HTTPStatusError
from PyPDF2 import PdfReader
from langchain.schema import BaseRetriever
import numpy as np
from pydantic import Field
from typing import List, Any

# Load environment variables
load_dotenv()
MISTRAL_API_KEY = os.getenv("API_KEY")

# Configuration constants
MILVUS_URI = "./milvus/milvus_vector.db"
MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
data_dir = "./volumes"
CACHE_FILE = "./document_cache.pkl"

# Purpose: Define the custom retriever logic for filtering relevant documents
# Input: User query as a string
# Output: List of relevant documents above the threshold score
# Processing: Performs a similarity search on the vector store, filters documents based on score threshold
class ScoreThresholdRetriever(BaseRetriever):
    vector_store: Any = Field(..., description="Vector store for similarity search")
    score_threshold: float = Field(default=0.1, description="Minimum score threshold for a document to be considered relevant")
    k: int = Field(default=1, description="Number of documents to retrieve")

    def get_relevant_documents(self, query:str) -> List[Any]:
        """
        Retrieve documents relevant to the query with a normalized score above the threshold.

        Args:
            query (str): Query string for searching the vector store.

        Returns:
            List[Document]: List of documents meeting the relevance criteria.
        """
        try:
            docs_and_scores = self.vector_store.similarity_search_with_score(query, k=self.k)
        except Exception as e:
            print(f"Error during similarity search: {e}")
            return [] # Return an empty list on search failure

        if not docs_and_scores:
            return [] # Handle cases where no documents are retrieved

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
        Normalize the score to a range of [0, 1].

        Args:
            score (float): Raw similarity score.

        Returns:
            float: Normalized similarity score.
        """
        # Assuming Milvus L2 distance, adjust based on your distance metric
        max_distance = np.sqrt(2)
        normalized = 1 - (score / max_distance)
        return max(0, min(1, normalized))

# Purpose: Initialize the HuggingFace embedding function
# Input: None
# Output: Embedding function instance
# Processing: Loads the HuggingFaceEmbeddings with a predefined model name
def get_embedding_function():
    embedding_function = HuggingFaceEmbeddings(model_name=MODEL_NAME)
    return embedding_function

# Purpose: Load and process PDF files in batches
# Input: Directory path for PDFs and batch size
# Output: Yields a batch of documents extracted from PDFs
# Processing: Loads PDF files, processes pages into Document objects, and caches processed files
def load_pdfs_in_batches(data_dir, batch_size=20):
    
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
            try:
                reader = PdfReader(pdf_path)
            except Exception as e:
                print(f"Error reading PDF {pdf_path}: {e}")
                continue  # Skip to the next file

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

# Purpose: Generate a response using RAG (Retrieval-Augmented Generation) model
# Input: User query as a string
# Output: Response text with citations
# Processing: Loads model, sets up retrieval chain, and generates response using retrieved documents
def query_rag(query):
    
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
        if not relevant_docs:
            return '''I regret to inform you that I could not find relevant context for your query. However, I am equipped to provide information related to <a href="https://dl.acm.org/doi/10.1145/3597503">  
                    research papers</a>. Please do not hesitate to reach out with any inquiries regarding them.'''
                   
    
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
                link = f'<a href="/team4/?view=pdf&file={data_dir}/{source}&page={page}" target="_blank" style="color : white">[more_info]</a>'
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


# Purpose: Create the prompt template for the RAG model
# Input: None
# Output: PromptTemplate object for the model
# Processing: Defines a static template for generating answers to user queries
def create_prompt():
    
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

# Purpose: Initialize the vector store for the RAG model
# Input: URI string (optional), path to the local Milvus database
# Output: Vector store created or loaded
# Processing: Loads PDF documents in batches, splits them into chunks, and stores them in a Milvus vector store
def initialize_milvus(uri: str=MILVUS_URI):

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

# Purpose: Split documents into smaller chunks for better processing
# Input: List of Document objects
# Output: List of chunked Document objects
# Processing: Uses a text splitter to break large documents into smaller, more manageable chunks
def split_documents(documents):
    
    # Create a text splitter to split the documents into chunks
    text_splitter = RecursiveCharacterTextSplitter(
        # Constants for embedding and chunking
        chunk_size=2000,  # Split the text into chunks of 1000 characters
        chunk_overlap=200,  # Overlap the chunks by 300 characters
        is_separator_regex=False,  # Don't split on regex
    )
    # Split the documents into chunks
    docs = text_splitter.split_documents(documents)
    return docs

# Purpose: Initialize a Milvus vector store using documents and embeddings
# Input: List of Document objects, embeddings function, URI string
# Output: The created or loaded vector store
# Processing: Connects to Milvus database, creates a collection, and stores the documents
def create_vector_store(docs, embeddings, uri):
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

# Purpose: Load an existing vector store from the local Milvus database
# Input: URI string (optional), path to the local Milvus database
# Output: Loaded vector store
# Processing: Connects to the existing Milvus database and loads the vector store
def load_exisiting_db(uri=MILVUS_URI):
    
    # Load an existing vector store
    vector_store = Milvus(
        collection_name="research_paper_chatbot",
        embedding_function = get_embedding_function(),
        connection_args={"uri": uri},
    )
    print("Vector Store Loaded")
    return vector_store

# Purpose: Extract answer and source information from the RAG response
# Input: Dictionary containing 'answer' and 'context' keys
# Output: Formatted string containing the answer and up to 5 source references
# Processing: Parses the context for source information and formats the response
def get_answer_with_source(response):
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

# Hardcoded responses mapping
HARDCODED_RESPONSES = {
    "what papers do you have?": "Currently, I can help you with papers related to software engineering. I have 7 papers in total.These are the papers EGFE: End-to-end Grouping of Fragmented Elements in UI Designs with Multimodal Learning ,A Comprehensive Study of Learning-based Android Malware Detectors under Challenging Environments,UniLog: Automatic Logging via LLM and In-Context Learning,Predicting Performance and Accuracy of Mixed-Precision Programs for Precision Tuning,Large Language Models for Test-Free Fault Localization,Dataflow Analysis-Inspired Deep Learning for Efficient Vulnerability Detection,Toward Automatically Completing GitHubWorkflows",
    "which conferences are these papers from?": "The papers are from 2024 IEEE/ACM 46th International Conference on Software Engineering (ICSE '24)",
    "what conferences proceedings can you help with?": "The papers are from 2024 IEEE/ACM 46th International Conference on Software Engineering (ICSE '24)",
    "how many papers do you know?": "I Know 7 papers in total,These are the papers EGFE: End-to-end Grouping of Fragmented Elements in UI Designs with Multimodal Learning ,A Comprehensive Study of Learning-based Android Malware Detectors under Challenging Environments,UniLog: Automatic Logging via LLM and In-Context Learning,Predicting Performance and Accuracy of Mixed-Precision Programs for Precision Tuning,Large Language Models for Test-Free Fault Localization,Dataflow Analysis-Inspired Deep Learning for Efficient Vulnerability Detection,Toward Automatically Completing GitHubWorkflows",
    "what are the papers do you know?": "These are the papers EGFE: End-to-end Grouping of Fragmented Elements in UI Designs with Multimodal Learning ,A Comprehensive Study of Learning-based Android Malware Detectors under Challenging Environments,UniLog: Automatic Logging via LLM and In-Context Learning,Predicting Performance and Accuracy of Mixed-Precision Programs for Precision Tuning,Large Language Models for Test-Free Fault Localization,Dataflow Analysis-Inspired Deep Learning for Efficient Vulnerability Detection,Toward Automatically Completing GitHubWorkflows",
}

def query_handler(query):
    """
    Handles user queries by checking for hardcoded responses first
    and falling back to the RAG model if no match is found.
    Args:
        query (str): User's query string.
    Returns:
        str: Response text for the query.
    """
    # Normalize the query for comparison
    normalized_query = query.lower().strip()

    # Check for hardcoded responses
    if normalized_query in HARDCODED_RESPONSES:
        return HARDCODED_RESPONSES[normalized_query]

    # If no hardcoded response is found, proceed with the RAG model
    return query_rag(query)


if __name__ == '__main__':
    pass