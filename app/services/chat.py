from app.services.embedding import get_embedding
from app.services.vector_store import search_similar
from app.services.audit import log_audit
from app.services.action_logs import log_action
from app.models.type import ChatState
import uuid
import time
import os
from loguru import logger
from app.core.config import USER_PROMPT

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver

# LOAD ENVIRONMENT
MODEL_TEMPERATURE = float(os.getenv("MODEL_TEMPERATURE"))
LLM_MODEL_NAME = os.getenv("LLM_MODEL_NAME")
MAX_OUTPUT_TOKEN = int(os.getenv("MAX_OUTPUT_TOKEN"))
TOP_K = int(os.getenv("TOP_K"))
MIN_SIM_SCORE = float(os.getenv("MIN_SIM_SCORE"))

chat_model = ChatGoogleGenerativeAI(model="gemini-2.0-flash",
                                    temperature=MODEL_TEMPERATURE,
                                    model_kwargs={
                                        "streaming": True,
                                        "max_output_tokens": MAX_OUTPUT_TOKEN
                                    })

async def direct_answer(state: ChatState):
    context = "\n".join([doc["content"] for doc in state["docs"]])
    prompt = f"Context:\n{context}\n\nQuestion: {state['query']}\nGive a concise answer."
    res = await chat_model.ainvoke([HumanMessage(content=prompt)])
    state["answer"] = res.content
    return state

async def retrieve_docs(state: ChatState):
    logger.info("Retrieving similar documents...")
    state["docs"] = await search_similar(
        query_emb=await get_embedding(state["query"]),
        k=TOP_K,
        min_sim_score=MIN_SIM_SCORE
    )
    return state

async def reasoning_step(state: ChatState):
    logger.info("Reasoning with context...")
    context = "\n".join([doc["content"] for doc in state["docs"]])
    reasoning_prompt = (
        f"Context:\n{context}\n\n"
        f"Question: {state['query']}\n"
        "Explain step-by-step reasoning before giving the final answer."
    )
    reasoning = await chat_model.ainvoke([HumanMessage(content=reasoning_prompt)])
    state["reasoning"] = reasoning.content
    return state

async def final_answer(state: ChatState):
    logger.info("Generating final concise answer...")
    answer_prompt = (
        f"Reasoning:\n{state['reasoning']}\n\n"
        "Now give a short and direct answer based on the reasoning."
    )
    answer = await chat_model.ainvoke([HumanMessage(content=answer_prompt)])
    state["answer"] = answer.content
    return state

def should_reasoning(state: ChatState) -> str:
    return "reasoning_step" if state.get("enable_reasoning", True) else "direct_answer"

# Build Reasoning Graph
workflow = StateGraph(ChatState)
workflow.add_node("retrieve_docs", retrieve_docs)
workflow.add_node("reasoning_step", reasoning_step)
workflow.add_node("direct_answer", direct_answer)
workflow.add_node("final_answer", final_answer)
workflow.add_edge(START, "retrieve_docs")
workflow.add_conditional_edges(
    "retrieve_docs",
    should_reasoning,
    {
        "reasoning_step": "reasoning_step",
        "direct_answer": "direct_answer"
    }
)
workflow.add_edge("reasoning_step", "final_answer")
workflow.add_edge("direct_answer", END)
workflow.add_edge("final_answer", END)

graph = workflow.compile(checkpointer=MemorySaver())

#---------Confident Score-----------

CONFIDENCE_PROMPT_TEMPLATE = """
    You are an impartial judge evaluating whether an AI-generated answer is factually supported by a given context.

    Here is the context provided to the AI:
    ---CONTEXT---
    {context_str}
    ---END CONTEXT---

    Here is the user's question:
    ---QUESTION---
    {question}
    ---END QUESTION---

    Here is the AI's generated answer:
    ---ANSWER---
    {response}
    ---END ANSWER---

    Your task is to determine a confidence score from 0.0 to 1.0, where:
    - 1.0 means the answer is fully and verifiably supported by the information in the CONTEXT.
    - 0.0 means the answer is not at all supported by the information in the CONTEXT.

    Please provide ONLY the numerical score and nothing else.
    """

async def calculate_confidence_score(context: str, question: str, response: str) -> float:
    """Calculates the confidence score of an AI-generated answer based on context."""
    prompt = CONFIDENCE_PROMPT_TEMPLATE.format(
        context_str=context,
        question=question,
        response=response
    )
    try:
        res = await chat_model.ainvoke([HumanMessage(content=prompt)])
        score_str = res.content.strip()
        return float(score_str)
    except Exception as e:
        logger.error(f"Error calculating confidence score: {e}")
        return 0.0

async def handle_chat(query: str, enable_reasoning: bool = True):
    start = time.time()
    chat_id = str(uuid.uuid4())

    async def generator():
        output = ""
        reasoning_text = ""
        first_token_latency = None
        docs = []
        final_state = None
        confidence_score = 0.0

        # Execute the graph and collect the final state
        async for state in graph.astream(
            {
                "query": query,
                "chat_id": chat_id,
                "enable_reasoning": enable_reasoning
            },
            config={"configurable": {"thread_id": chat_id}}
        ):
            # Update final_state with the latest state
            final_state = state
            
            # Capture docs as soon as retrieved
            if "retrieve_docs" in state and state["retrieve_docs"].get("docs"):
                docs = [doc["content"] for doc in state["retrieve_docs"]["docs"]]

        # After graph execution, get the final answer and stream it
        if final_state:
            # Extract the final answer based on the path taken
            if enable_reasoning and "final_answer" in final_state:
                answer_content = final_state["final_answer"].get("answer", "")
                reasoning_text = final_state["final_answer"].get("reasoning", "")
            elif "direct_answer" in final_state:
                answer_content = final_state["direct_answer"].get("answer", "")
            else:
                answer_content = ""

            # Stream the answer token by token
            first_token_latency = int((time.time() - start) * 1000)
            for char in answer_content:
                yield char
                output += char
            # context_for_confidence = "\n".join([doc[i] for i,doc in enumerate(docs)])
            confidence_score = await calculate_confidence_score(str(docs), query, output)
            logger.info(confidence_score)
            logger.info(docs)


        await log_audit(
            chat_id=chat_id,
            question=query,
            response=output,
            retrieved_docs=docs,
            latency_ms=first_token_latency,
            model_confident=confidence_score
        )
        
        total_latency = int((time.time() - start) * 1000)
        await log_action(
            action_type="chat",
            resource_type="llm",
            resource_id=chat_id,
            request_data={
                "query": query,
                "enable_reasoning": enable_reasoning,
                "docs": docs
            },
            response_data={
                "answer": output,
                "reasoning": reasoning_text,
                "model_confident": confidence_score
            },
            latency_ms=total_latency,
            status="success"
        )
    
    return generator()