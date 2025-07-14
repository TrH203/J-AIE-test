from sqlalchemy import delete, select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_session
from app.models.document import Document
from app.services.embedding import get_embedding
import numpy as np

async def upsert_docs(docs: list[dict]):
    async with get_session() as session:
        for doc in docs:
            vec = await get_embedding(doc["text"])
            stmt = insert(Document).values(
                id=doc["id"],
                content=doc["text"],
                embedding=vec
            ).on_conflict_do_update(
                index_elements=["id"],
                set_={"content": doc["text"], "embedding": vec}
            )
            await session.execute(stmt)
        await session.commit()
        return {"status": "success"}

async def delete_doc(doc_id: str):
    async with get_session() as session:
        # Check if the document exists
        result = await session.execute(select(Document).where(Document.id == doc_id))
        doc = result.scalar_one_or_none()

        if not doc:
            return {"success": False, "message": f"No document found with id '{doc_id}'"}

        # Delete the document
        await session.execute(delete(Document).where(Document.id == doc_id))
        await session.commit()
        return {"success": True, "deleted": doc_id}

async def list_docs():
    async with get_session() as session:
        result = await session.execute(select(Document))
        docs = result.scalars().all()
        return [{"id": d.id, "created_at": d.created_at,"content": d.content, "size": len(d.content)} for d in docs]

async def search_similar(query_emb: list[float], k: int = 3):
    async with get_session() as session:
        q = f"""
        SELECT id, content FROM documents
        ORDER BY embedding <-> :embedding
        LIMIT :k
        """
        result = await session.execute(q, {"embedding": np.array(query_emb), "k": k})
        return result.fetchall()
