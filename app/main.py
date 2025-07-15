from fastapi import FastAPI
from app.api import chat, knowledge, audit, logs
from app.core.database import engine
from app.models.document import Base as DocBase
from app.models.audit import Base as AuditBase
from app.models.action_log import Base as ActionLogBase
from sqlalchemy import text
from dotenv import load_dotenv
from loguru import logger
import os

load_dotenv()

# Initialize FastAPI app
app = FastAPI()

app.include_router(knowledge.router, prefix="/knowledge")
app.include_router(chat.router, prefix="/chat")
app.include_router(audit.router, prefix="/audit")
app.include_router(logs.router, prefix="/logs", tags=["Logs"])

@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector;"))

        await conn.run_sync(DocBase.metadata.create_all)
        await conn.run_sync(AuditBase.metadata.create_all)
        await conn.run_sync(ActionLogBase.metadata.create_all)
        
        lists = int(os.getenv("PGVECTOR_LISTS", 100))
        await conn.execute(text(f"""
            CREATE INDEX IF NOT EXISTS documents_embedding_idx
            ON documents
            USING ivfflat (embedding vector_cosine_ops)
            WITH (lists = {lists});
        """))

        await conn.execute(text("ANALYZE documents;"))

        logger.info("Pgvector installed, tables created, and IVFFlat index optimized.")
