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
from data import CORPUS_SOURCE
from langchain_community.document_loaders import PyPDFDirectoryLoader
from roman import toRoman
from PyPDF2 import PdfReader

load_dotenv()
MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")

MILVUS_URI = "./milvus/milvus_vector.db"
MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
data_dir = "./volumes"

CACHE_FILE = "./document_cache.pkl"

def get_embedding_function():
    return HuggingFaceEmbeddings(model_name=MODEL_NAME)

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

def split_documents(documents):
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=2000,
        chunk_overlap=200,
    )
    return text_splitter.split_documents(documents)

def create_vector_store(docs, embeddings, uri):
    os.makedirs(os.path.dirname(uri), exist_ok=True)
    connections.connect("default", uri=uri)

    if utility.has_collection("research_paper_chatbot"):
        print("Loading existing collection...")
        vector_store = Milvus(
            collection_name="research_paper_chatbot",
            embedding_function=embeddings,
            connection_args={"uri": uri}
            
        )
    else:
        vector_store = Milvus.from_documents(
            documents=docs,
            embedding=embeddings,
            collection_name="research_paper_chatbot",
            connection_args={"uri": uri},
            drop_old=True,
        )
    return vector_store

def initialize_milvus(uri=MILVUS_URI):
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

def query_rag(query):
    """
    Entry point for the RAG model to generate an answer to a given query

    This function initializes the RAG model, sets up the necessary components such as the prompt template, vector store, 
    retriever, document chain, and retrieval chain, and then generates a response to the provided query.

    Args:
        query (str): The query string for which an answer is to be generated.
    
    Returns:
        str: The answer to the query
    """
    # Define the model
    model = ChatMistralAI(model='open-mistral-7b',api_key=MISTRAL_API_KEY)
    print("Model Loaded")

    prompt = create_prompt()

    # Load the vector store and create the retriever
    vector_store = load_exisiting_db(uri=MILVUS_URI)
    retriever = vector_store.as_retriever()
    try:
        document_chain = create_stuff_documents_chain(model, prompt)
        print("Document Chain Created")

        retrieval_chain = create_retrieval_chain(retriever, document_chain)
        print("Retrieval Chain Created")
    
        # Generate a response to the query
        response = retrieval_chain.invoke({"input": f"{query}"})
    except HTTPStatusError as e:
        print(f"HTTPStatusError: {e}")
        if e.response.status_code == 429:
            return "I am currently experiencing high traffic. Please try again later.", []
        #return "I am unable to answer this question at the moment. Please try again later.", []
        return f"HTTPStatusError: {e}", [] 

    return get_answer_with_source(response)



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
#   pdf_path = "./volumes"
  answer = response.get('answer', 'No answer found.') # Extract the answer
  sources = [] # Handle multiple contexts in the response (assuming response['context'] is a list)
  # Iterate over context documents and get top 5 sources
  for doc in response.get("context", [])[:5]:
    page = doc.metadata.get('page', 'Unknown page')
    print(page)
    source_pdf = doc.metadata.get('source', '').split('/')[-1]  # Get only the file name from the path
    print(source_pdf,flush=True)
        # Adjust the page index and create a link to open the PDF at a specific page
    if page != 'Unknown page':
            # page += 1  # Adjust to be 1-based indexing if necessary
            link = f'<a href="/team4/?view=pdf&file={data_dir}/{source_pdf}&page={page + 1}" target="_blank">[{page + 1}]</a>'
            # link = f"[Page {page} in {source_pdf}](/team4/?view=pdf&file={data_dir}/{source_pdf}&page={page})"
    else:
            link = f"[Source: {source_pdf}]"

    sources.append(link)

    # Format all sources with Markdown-compatible newline breaks
    sources_info = "\n\nSources:\n" + "\n".join(sources)
    return f"{answer}\n\n{sources_info}"

if __name__ == '__main__':
    pass