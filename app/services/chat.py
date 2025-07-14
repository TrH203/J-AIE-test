from app.services.embedding import get_embedding
from app.services.vector_store import search_similar
from app.services.audit import log_audit
from datetime import datetime
import uuid
import time
import os

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage


MODEL_TEMPERATURE = os.getenv("MODEL_TEMPERATURE", 0.1)
LLM_MODEL_NAME = os.getenv("LLM_MODEL_NAME", "gemini-2.0-flash")

chat_model = ChatGoogleGenerativeAI(model=LLM_MODEL_NAME, temperature=float(MODEL_TEMPERATURE), model_kwargs={"streaming": True})

async def handle_chat(query: str):
    query_emb = await get_embedding(query)
    docs = await search_similar(query_emb)
    print(f"Found {len(docs)} documents for query: {query}")
    context = "\n".join([doc[1] for doc in docs])
    print(f"Context for query: {context}")
    chat_id = str(uuid.uuid4())
    start = time.time()

    stream = chat_model.astream([HumanMessage(content=f"{context}\n\nQuestion: {query}")])

    async def generator():
        output = ""
        async for chunk in stream:
            yield chunk.content
            output += chunk.content

        latency = int((time.time() - start) * 1000)
        await log_audit(chat_id, query, output, [doc[1] for doc in docs], latency)

    return generator()
