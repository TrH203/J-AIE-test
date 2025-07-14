from fastapi import APIRouter, Request
from fastapi.responses import StreamingResponse
from app.services.chat import handle_chat

router = APIRouter()

@router.post("")
async def chat_stream(request: Request):
    data = await request.json()
    return StreamingResponse(handle_chat(data["query"]), media_type="text/event-stream")
