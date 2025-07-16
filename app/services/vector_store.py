from sqlalchemy import delete, select, text
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.exc import SQLAlchemyError
from app.core.database import get_session
from app.models.document import Document
from app.services.embedding import get_embedding
from app.services.action_logs import log_action
import time
import json
import uuid
from loguru import logger

async def upsert_docs(docs: list[dict]):
    async with get_session() as session:
        results = []
        try:
            for doc in docs:
                doc["id"] = doc.get("id", str(uuid.uuid4()))
                start = time.time()
                
                if "text" not in doc:
                    results.append({"id": doc["id"], "action": "failed", "reason": "Missing 'text'"})

                    await log_action(
                        action_type="upsert",
                        resource_type="document",
                        resource_id=doc.get("id"),
                        request_data=doc,
                        status="failed",
                        error_message=reason
                    )
                    continue

                exists = await session.execute(select(Document.id).where(Document.id == doc["id"]))
                exists = exists.scalar_one_or_none()

                try:
                    vec = await get_embedding(doc["text"])
                except Exception as e:
                    reason = f"Embedding error: {str(e)}"
                    logger.error(reason)
                    results.append({"id": doc["id"], "action": "failed", "reason": reason})

                    await log_action(
                        action_type="upsert",
                        resource_type="document",
                        resource_id=doc["id"],
                        request_data={"text": doc["text"]},
                        status="failed",
                        error_message=reason
                    )
                    continue

                try:
                    stmt = insert(Document).values(
                        id=doc["id"],
                        content=doc["text"],
                        embedding=vec,
                        extra_info=doc.get("extra_info", {}),
                    ).on_conflict_do_update(
                        index_elements=["id"],
                        set_={"content": doc["text"], "embedding": vec, "extra_info": doc.get("extra_info", {})}
                    )
                    await session.execute(stmt)

                    action = "updated" if exists else "inserted"
                    latency = int((time.time() - start) * 1000)

                    results.append({"id": doc["id"], "action": action})

                    await log_action(
                        action_type=action,
                        resource_type="document",
                        resource_id=doc["id"],
                        request_data={"text": doc["text"]},
                        latency_ms=latency,
                        status="success"
                    )

                except SQLAlchemyError as e:
                    reason = f"Database error: {str(e)}"
                    logger.error(reason)
                    results.append({"id": doc["id"], "action": "failed", "reason": reason})

                    await log_action(
                        action_type="upsert",
                        resource_type="document",
                        resource_id=doc["id"],
                        request_data={"text": doc["text"]},
                        status="failed",
                        error_message=reason
                    )
                    continue

            await session.commit()
            return {"status": "success", "results": results}

        except SQLAlchemyError as e:
            await session.rollback()
            logger.error(f"Database error during bulk upsert: {e}")
            return {"status": "error", "message": f"Database error: {str(e)}"}

        except Exception as e:
            await session.rollback()
            logger.error(f"Unexpected error during bulk upsert: {e}")
            return {"status": "error", "message": f"Unexpected error: {str(e)}"}


async def delete_doc(doc_id: str):
    async with get_session() as session:
        start = time.time()
        try:
            result = await session.execute(select(Document).where(Document.id == doc_id))
            doc = result.scalar_one_or_none()

            if not doc:
                await log_action(
                    action_type="delete",
                    resource_type="vector_store",
                    resource_id=doc_id,
                    status="failed",
                    error_message=f"No document found with id '{doc_id}'"
                )
                return {"success": False, "message": f"No document found with id '{doc_id}'"}

            await session.execute(delete(Document).where(Document.id == doc_id))
            await session.commit()

            latency = int((time.time() - start) * 1000)

            await log_action(
                action_type="delete",
                resource_type="vector_store",
                resource_id=doc_id,
                request_data={"content": doc.content},
                latency_ms=latency,
                status="success"
            )

            return {"success": True, "deleted": doc_id}

        except SQLAlchemyError as e:
            await session.rollback()
            logger.error(f"Database error while deleting doc {doc_id}: {e}")
            await log_action(
                action_type="delete",
                resource_type="vector_store",
                resource_id=doc_id,
                status="failed",
                error_message=f"Database error: {str(e)}"
            )
            return {"success": False, "message": f"Database error: {str(e)}"}

        except Exception as e:
            await session.rollback()
            logger.error(f"Unexpected error while deleting doc {doc_id}: {e}")
            await log_action(
                action_type="delete",
                resource_type="vector_store",
                resource_id=doc_id,
                status="failed",
                error_message=f"Unexpected error: {str(e)}"
            )
            return {"success": False, "message": f"Unexpected error: {str(e)}"}

async def list_docs():
    async with get_session() as session:
        try:
            result = await session.execute(select(Document))
            docs = result.scalars().all()

            response_data = [
                {
                    "id": d.id,
                    "created_at": d.created_at,
                    "content": d.content,
                    "size": len(d.content)
                }
                for d in docs
            ]

            await log_action(
                action_type="list",
                resource_type="document",
                request_data={},  # No input for list
                response_data={"count": len(response_data)},
                status="success"
            )

            return response_data

        except Exception as e:
            await log_action(
                action_type="list",
                resource_type="document",
                status="failed",
                error_message=str(e)
            )

            return {"status": "error", "message": str(e)}

async def search_knowledge_by_id(knowledge_id: str):
    async with get_session() as session:
        result = await session.execute(select(Document).where(Document.id == knowledge_id))
        log = result.scalar_one_or_none()

        if not log:
            return {}

        return {
            "id": log.id,
            "content": log.content,
            "created_at": log.created_at,
            "extra_info": log.extra_info,
        }

async def search_similar(query_emb: list[float], k: int = 3, min_sim_score: float = 0.5):
    async with get_session() as session:
        try:
            start = time.time()
            query_embedding_str = json.dumps(query_emb)
            q = text("""
                SELECT id, content, 1 - (embedding <-> (:query_embedding_str)::vector) AS similarity
                FROM documents
                WHERE 1 - (embedding <-> (:query_embedding_str)::vector) > :min_sim_score
                ORDER BY similarity DESC
                LIMIT :k
            """)
            result = await session.execute(
                q,
                {
                    "query_embedding_str": query_embedding_str,
                    "min_sim_score": min_sim_score,
                    "k": k
                }
            )
            rows = result.fetchall()

            response_data = [
                {
                    "id": r[0],
                    "content": r[1],
                    "similarity": float(r[2])
                }
                for r in rows
            ]
            latency = int((time.time() - start) * 1000)
            await log_action(
                action_type="search",
                resource_type="vector_store",
                request_data={
                    "k": k,
                    "min_sim_score": min_sim_score
                },
                response_data={"results_count": len(response_data), "retrived_docs": response_data},
                latency_ms=latency
            )

            return response_data

        except SQLAlchemyError as e:
            logger.error(f"Database error during search: {e}")
            await log_action(
                action_type="search",
                resource_type="vector_store",
                request_data={"k": k, "min_sim_score": min_sim_score},
                status="failed",
                error_message=f"Database error: {str(e)}"
            )
            return {"status": "error", "message": f"Database error: {str(e)}"}

        except Exception as e:
            logger.error(f"Unexpected error during search: {e}")
            await log_action(
                action_type="search",
                resource_type="vector_store",
                request_data={"k": k, "min_sim_score": min_sim_score},
                status="failed",
                error_message=f"Unexpected error: {str(e)}"
            )
            return {"status": "error", "message": f"Unexpected error: {str(e)}"}