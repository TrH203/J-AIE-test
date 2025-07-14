from fastapi import FastAPI
from app.api import chat, knowledge, audit
from app.core.database import engine
from app.models.document import Base as DocBase
from app.models.audit import Base as AuditBase
from sqlalchemy import text
from dotenv import load_dotenv

load_dotenv()
# Initialize FastAPI app
app = FastAPI()

app.include_router(knowledge.router, prefix="/knowledge")
app.include_router(chat.router, prefix="/chat")
app.include_router(audit.router, prefix="/audit")

@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        # Ensure pgvector is installed
        await conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector;"))

        # Auto-create tables
        await conn.run_sync(DocBase.metadata.create_all)
        await conn.run_sync(AuditBase.metadata.create_all)
        print("pgvector installed and tables created.")