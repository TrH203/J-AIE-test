from fastapi import APIRouter, HTTPException
from app.services.audit import list_audit_logs, search_audit_by_id

router = APIRouter()

@router.get("/{chat_id}")
async def get_audit_by_id_route(chat_id: str):
    log = await search_audit_by_id(chat_id)
    if not log:
        raise HTTPException(status_code=404, detail="Audit log not found")
    return log

@router.get("/")
async def get_all_audits():
    return await list_audit_logs()