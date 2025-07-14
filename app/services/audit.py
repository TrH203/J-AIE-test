from sqlalchemy import insert
from app.models.audit import AuditLog
from app.core.database import get_session
from datetime import datetime

async def log_audit(chat_id: str, question: str, response: str, retrieved_docs: list[str], latency_ms: int):
    async with get_session() as session:
        stmt = insert(AuditLog).values(
            chat_id=chat_id,
            question=question,
            response=response,
            retrieved_docs=retrieved_docs,
            latency_ms=latency_ms,
            timestamp=datetime.utcnow()
        )
        await session.execute(stmt)
        await session.commit()
