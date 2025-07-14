from fastapi import APIRouter

router = APIRouter()

@router.get("/{chat_id}")
async def get_audit(chat_id: str):
    # Placeholder - get from DB
    return {"chat_id": chat_id}
