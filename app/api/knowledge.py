from fastapi import APIRouter, HTTPException, UploadFile, File
import uuid
from app.services.vector_store import upsert_docs, delete_doc, list_docs
from app.services.file_extractor import extract_text
import shutil
import tempfile
import os
router = APIRouter()

@router.post("/update")
async def update_knowledge(docs: list[dict]):
    return await upsert_docs(docs)

@router.delete("/{doc_id}")
async def delete_knowledge(doc_id: str):
    return await delete_doc(doc_id)

@router.get("")
async def get_knowledge():
    return await list_docs()

@router.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    file_ext = os.path.splitext(file.filename)[-1].lower()

    with tempfile.NamedTemporaryFile(delete=False, suffix=file_ext) as tmp:
        shutil.copyfileobj(file.file, tmp)
        tmp_path = tmp.name

    docs = await extract_text(tmp_path, file_ext)
    
    os.remove(tmp_path)
    return await upsert_docs(docs)
