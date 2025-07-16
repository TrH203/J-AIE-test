from fastapi import APIRouter, Request
from fastapi.responses import StreamingResponse
from app.services.chat import handle_chat

router = APIRouter()

@router.post("")
async def chat_stream(request: Request):
    """
    Using request to chat realtime:
    Input example:
    {"text": "Tell me about AI", enable_reasoning: true(default=false)}
    """
    data = await request.json()
    generator = await handle_chat(data["query"], enable_reasoning=data.get("enable_reasoning", False))
    return StreamingResponse(generator, media_type="text/event-stream")

