import pathlib
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_qdrant import QdrantVectorStore
from dotenv import load_dotenv

path = pathlib.Path(__file__).parent.resolve() / "data_files/The_Courage_to_be_Disliked_How_to_Change_Your_Life_and_Achieve_Real.pdf"
load_dotenv()

def load_pdf(file_path: str):
    # load the PDF file using PyPDFLoader
    loader = PyPDFLoader(file_path)
    docs = loader.load()
    return docs

def split_documents(documents, chunk_size=1000, chunk_overlap=200):
    # split the documents into smaller chunks using RecursiveCharacterTextSplitter
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    chunks = text_splitter.split_documents(documents)
    return chunks

def embed_documents(chunks):
    # embed the chunks using HuggingFaceEmbeddings
    embeddings = HuggingFaceEmbeddings(
        model_name="all-MiniLM-L6-v2",
    )

    # create a vector store using QdrantVectorStore and store the embedded chunks
    vector_store = QdrantVectorStore.from_documents(
        documents=chunks,
        embedding=embeddings,
        url= "http://localhost:6333",
        collection_name= "rag-learning"
    )
    return vector_store


def index():
    file_path = "data_files/The_Courage_to_be_Disliked_How_to_Change_Your_Life_and_Achieve_Real.pdf"
    documents = load_pdf(file_path)
    # print(f"Loaded {len(documents)} documents from the PDF.")

    chunks = split_documents(documents)
    # print(f"Split the documents into {len(chunks)} chunks.")

    embed_documents(chunks)
    # print("Embedded the chunks and stored them in the vector store.")