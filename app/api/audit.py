from fastapi import APIRouter, HTTPException, Query
from app.services.audit import list_audit_logs, search_audit_by_id

router = APIRouter()

@router.get("/{chat_id}")
async def get_audit_by_id_route(chat_id: str):
    log = await search_audit_by_id(chat_id=chat_id)
    if not log:
        raise HTTPException(status_code=404, detail="Audit log not found")
    return log

@router.get("/")
async def get_all_audits(
        skip: int = Query(0, ge=0),
        limit: int = Query(50, ge=10, le=100)):
    """
    Example: /audit?skip=0&limit=20
    """
    return await list_audit_logs(limit=limit, skip=skip)