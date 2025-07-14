from fastapi import APIRouter, HTTPException
from app.services.vector_store import upsert_docs, delete_doc, list_docs

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
