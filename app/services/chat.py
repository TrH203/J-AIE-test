from app.services.embedding import get_embedding
from app.services.vector_store import search_similar
from app.services.audit import log_audit
from app.services.action_logger import log_action
import uuid
import time
import os
from loguru import logger
from app.core.config import USER_PROMPT

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage

# LOAD ENVIRONMENT
MODEL_TEMPERATURE = float(os.getenv("MODEL_TEMPERATURE"))
LLM_MODEL_NAME = os.getenv("LLM_MODEL_NAME")
MAX_OUTPUT_TOKEN = int(os.getenv("MAX_OUTPUT_TOKEN"))
TOP_K = int(os.getenv("TOP_K"))
MIN_SIM_SCORE = float(os.getenv("MIN_SIM_SCORE"))

chat_model = ChatGoogleGenerativeAI(model=LLM_MODEL_NAME,
                                    temperature=MODEL_TEMPERATURE,
                                    model_kwargs={
                                        "streaming": True,
                                        "max_output_tokens": MAX_OUTPUT_TOKEN
                                    })

async def handle_chat(query: str):
    start = time.time()
    chat_id = str(uuid.uuid4())

    try:
        query_emb = await get_embedding(text=query)

        response_data = await search_similar(query_emb=query_emb, k=TOP_K, min_sim_score=MIN_SIM_SCORE)
        context = USER_PROMPT + "\nContext for question:\n - " + "\n - ".join([r["content"] for r in response_data])

        stream = chat_model.astream([
            HumanMessage(content=f"{context}\n\nQuestion: {query}")
        ])

        async def generator():
            output = ""
            first_token_latency = None

            async for chunk in stream:
                if first_token_latency is None:
                    first_token_latency = int((time.time() - start) * 1000)
                    logger.info(f"First token latency: {first_token_latency} ms")

                yield chunk.content
                output += chunk.content

            total_latency = int((time.time() - start) * 1000)

            await log_audit(
                chat_id=chat_id,
                question=query,
                response=output,
                retrieved_docs=[r["content"] for r in response_data],
                latency_ms=total_latency
            )

            await log_action(
                action_type="chat",
                resource_type="llm",
                resource_id=chat_id,
                request_data={"query": query, "context": context},
                response_data={"answer": output, "docs_count": len(response_data)},
                latency_ms=total_latency,
                status="success"
            )

        return generator()

    except Exception as e:
        logger.error(f"Error during chat handling: {e}")

        await log_action(
            action_type="chat",
            resource_type="llm",
            resource_id=chat_id,
            request_data={"query": query},
            status="failed",
            error_message=str(e)
        )
        raise e

