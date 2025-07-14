from sqlalchemy import text
from app.core.database import engine
import asyncio

async def test_connection():
    async with engine.begin() as conn:
        # PostgreSQL version
        await conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector;"))
        print("pgvector extension installed.")

        result = await conn.execute(text("SELECT version();"))
        print("PostgreSQL version:", result.scalar())

        # pgvector extension check
        result = await conn.execute(text("SELECT extname FROM pg_extension WHERE extname = 'vector';"))
        ext = result.fetchone()
        if ext:
            print("pgvector extension is installed")
        else:
            print("pgvector extension NOT found")

        # list tables
        result = await conn.execute(text("""
            SELECT table_name FROM information_schema.tables
            WHERE table_schema='public';
        """))
        tables = result.scalars().all()
        print("Tables:", tables)


if __name__ == "__main__":
    asyncio.run(test_connection())
