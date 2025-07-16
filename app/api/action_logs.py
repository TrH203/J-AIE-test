from fastapi import APIRouter, HTTPException, Query
from app.services.action_logs import list_all_action_logs
from app.services.action_logs import search_log_by_id
from app.models.type import LogsStatus, LogsActionType
router = APIRouter()

@router.get("/")
async def get_all_logs(
        skip: int = Query(0, ge=0),
        limit: int = Query(50, ge=1, le=500),
        action_type: LogsActionType | None = None,
        resource_type: str | None = None,
        status: LogsStatus | None = None,
    ):
    """
    Get logs with pagination and optional filters.
    Example: /logs?skip=0&limit=20&action_type=chat
    """
    log = await list_all_action_logs(skip=skip,
                                     limit=limit,
                                     action_type=action_type.value if action_type else None,
                                     resource_type=resource_type,
                                     status=status.value if status else None)
    return log

@router.get("/{log_id}")
async def get_log_by_id(log_id: str):
    """
    Get a single action log by its ID
    Example: /logs/{log_id}
    """
    return await search_log_by_id(log_id=log_id)