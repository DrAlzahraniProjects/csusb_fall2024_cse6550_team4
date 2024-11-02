import os
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

load_dotenv()
MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")

MILVUS_URI = "./milvus/milvus_vector.db"
MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
data_dir = "./volumes"

def get_embedding_function():
    """
    returns embedding function for the model

    Returns:
        embedding function
    """
    embedding_function = HuggingFaceEmbeddings(model_name=MODEL_NAME)
    return embedding_function


def load_pdfs(data_dir):
    loader = PyPDFDirectoryLoader(data_dir)
    documents = loader.load()
    for doc in documents:
        if "paper1.pdf" in doc.metadata["source"]:
            doc.metadata["source"] = "https://dl.acm.org/doi/10.1145/3597503.3649398"
        elif "paper2.pdf" in doc.metadata["source"]:
            doc.metadata["source"] = "https://dl.acm.org/doi/10.1145/3597503.3649399"
    return documents


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
    
    # logic to add sources to the response
    # max_relevant_sources = 4 # number of sources at most to be added to the response
    # all_sources = ""
    # sources = []
    # count = 1
    # for i in range(max_relevant_sources):
    #     try:
    #         source = response["context"][i].metadata["source"]
    #         # check if the source is already added to the list
    #         if source not in sources:
    #             sources.append(source)
    #             all_sources += f"[Source {count}]({source}), "
    #             count += 1
    #     except IndexError: # if there are no more sources to add
    #         break
    # all_sources = all_sources[:-2] # remove the last comma and space
    # response["answer"] += f"\n\nSources: {all_sources}"
    # print("Response Generated")

    # return response["answer"], sources
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


def initialize_milvus(uri: str=MILVUS_URI):
    """
    Initialize the vector store for the RAG model

    Args:
        uri (str, optional): Path to the local milvus db. Defaults to MILVUS_URI.

    Returns:
        vector_store: The vector store created
    """
    embeddings = get_embedding_function()
    print("Embeddings Loaded")
    # documents = load_documents_from_web()
    documents = load_pdfs(data_dir)
    print("Documents Loaded")
    print(len(documents))

    # Split the documents into chunks
    docs = split_documents(documents=documents)
    print("Documents Splitting completed")

    vector_store = create_vector_store(docs, embeddings, uri)

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
#   pdf_path = "./volumes"
  answer = response.get('answer', 'No answer found.') # Extract the answer
  sources = [] # Handle multiple contexts in the response (assuming response['context'] is a list)
  # Iterate over context documents and get top 5 sources
  for doc in response.get("context", [])[:5]:
    page = doc.metadata.get('page', 'Unknown page')
    print(page)
    source_pdf = doc.metadata.get('source', '').split('/')[-1]  # Get only the file name from the path

        # Adjust the page index and create a link to open the PDF at a specific page
    if page != 'Unknown page':
            page += 1  # Adjust to be 1-based indexing if necessary
            #link = f'<a href="/team4/?view=pdf&file={pdf_path}&page={page + 1}" target="_blank">[{page + 1}]</a>'
            link = f"[Page {page} in {source_pdf}](/team4/?view=pdf&file={data_dir}/{source_pdf}&page={page})"
    else:
            link = f"[Source: {source_pdf}]"

    sources.append(link)

    # Format all sources with Markdown-compatible newline breaks
    sources_info = "\n\nSources:\n" + "\n".join(sources)
    return f"{answer}\n\n{sources_info}"

if __name__ == '__main__':
    pass

