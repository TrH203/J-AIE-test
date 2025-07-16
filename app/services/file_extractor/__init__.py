from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from typing import List
import os
from dotenv import load_dotenv

load_dotenv()

CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", 500))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", 100))

text_splitter = RecursiveCharacterTextSplitter(chunk_size=CHUNK_SIZE, chunk_overlap=CHUNK_OVERLAP)

async def extract_text_from_pdf(file_path: str) -> List[str]:
    loader = PyPDFLoader(file_path)
    documents = loader.load()
    chunks = text_splitter.split_documents(documents)
    return [chunk.page_content for chunk in chunks]

async def extract_text_from_txt(file_path: str) -> List[str]:
    loader = TextLoader(file_path, encoding="utf-8")
    documents = loader.load()
    chunks = text_splitter.split_documents(documents)
    return [chunk.page_content for chunk in chunks]

async def extract_text(file_path: str, file_ext: str, file_name:str):
    """Auto choose extraction method based on file type."""
    if file_ext == ".pdf":
        docs = await extract_text_from_pdf(file_path)
    elif file_ext in [".txt", ".md"]:
        docs = await extract_text_from_txt(file_path)
    else:
        return []
    return [{"text": doc, "extra_info": {"filename": file_name}} for doc in docs]
