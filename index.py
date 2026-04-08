import pathlib
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

path = pathlib.Path(__file__).parent.resolve() / "data_files/The_Courage_to_be_Disliked_How_to_Change_Your_Life_and_Achieve_Real.pdf"

def load_pdf(file_path: str):
    # load the PDF file using PyPDFLoader
    loader = PyPDFLoader(file_path)
    docs = loader.load()
    return docs
