from sqlalchemy import insert
from app.models.audit import AuditLog
from app.core.database import get_session
from datetime import datetime
from sqlalchemy import select

async def log_audit(chat_id: str, question: str, response: str, retrieved_docs: list[str], latency_ms: int):
    async with get_session() as session:
        stmt = insert(AuditLog).values(
            chat_id=chat_id,
            question=question,
            response=response,
            retrieved_docs=retrieved_docs,
            latency_ms=latency_ms,
            timestamp=datetime.now(),
        )
        await session.execute(stmt)
        await session.commit()
        
async def search_audit_by_id(chat_id: str):
    async with get_session() as session:
        result = await session.execute(select(AuditLog).where(AuditLog.chat_id == chat_id))
        log = result.scalar_one_or_none()

        if not log:
            return None

        return {
            "chat_id": log.chat_id,
            "question": log.question,
            "response": log.response,
            "retrieved_docs": log.retrieved_docs,
            "latency_ms": log.latency_ms,
            "timestamp": log.timestamp,
            "feedback": log.feedback
        }

async def list_audit_logs():
    async with get_session() as session:
        result = await session.execute(select(AuditLog))
        logs = result.scalars().all()
        return [
            {
                "chat_id": log.chat_id,
                "question": log.question,
                "response": log.response,
                "retrieved_docs": log.retrieved_docs,
                "latency_ms": log.latency_ms,
                "timestamp": log.timestamp,
                "feedback": log.feedback
            }
            for log in logs
        ]
