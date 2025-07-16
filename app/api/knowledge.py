from fastapi import APIRouter, HTTPException, UploadFile, File
import uuid
from app.services.vector_store import upsert_docs, delete_doc, list_docs, search_knowledge_by_id
from app.services.file_extractor import extract_text
import shutil
import tempfile
import os
router = APIRouter()

@router.post("/update")
async def update_knowledge(docs: list[dict]):
    """
    Create or Update(if id existed)
    Example:
    - {"id": "uuid1", "text": "abc"} # Create
    - {"id": "uuid1", "text": "xyz"} # Update
    """
    return await upsert_docs(docs)

@router.delete("/{doc_id}")
async def delete_knowledge(doc_id: str):
    return await delete_doc(doc_id)

@router.get("")
async def get_knowledge():
    """
    Get all knowledge
    """
    return await list_docs()

@router.get("/{knowledge_id}")
async def get_knowledge_by_id(knowledge_id):
    return await search_knowledge_by_id(knowledge_id=knowledge_id)

@router.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    """
    Upload, chunking and embedding into vector database.
    File supported: .pdf, .md, .txt
    """
    file_ext = os.path.splitext(file.filename)[-1].lower()

    with tempfile.NamedTemporaryFile(delete=False, suffix=file_ext) as tmp:
        shutil.copyfileobj(file.file, tmp)
        tmp_path = tmp.name

    docs = await extract_text(file_path=tmp_path, file_ext=file_ext, file_name=file.filename)
    
    os.remove(tmp_path)
    return await upsert_docs(docs)
