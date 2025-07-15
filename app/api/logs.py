from fastapi import APIRouter, HTTPException, Query
from sqlalchemy import select
from app.models.action_log import ActionLog
from app.core.database import get_session

router = APIRouter()

@router.get("/")
async def get_all_logs(limit: int = Query(50, ge=1, le=500)):
    """
    Get all action logs (default last limit: 50)
    """
    async with get_session() as session:
        result = await session.execute(select(ActionLog).order_by(ActionLog.timestamp.desc()).limit(limit))
        logs = result.scalars().all()
        return [
            {
                "id": log.id,
                "action_type": log.action_type,
                "resource_type": log.resource_type,
                "resource_id": log.resource_id,
                "status": log.status,
                "latency_ms": log.latency_ms,
                "timestamp": log.timestamp,
            }
            for log in logs
        ]

@router.get("/{log_id}")
async def get_log_by_id(log_id: str):
    """
    Get a single action log by its ID
    """
    async with get_session() as session:
        result = await session.execute(select(ActionLog).where(ActionLog.id == log_id))
        log = result.scalar_one_or_none()
        if not log:
            raise HTTPException(status_code=404, detail=f"Log with id '{log_id}' not found")

        return {
            "id": log.id,
            "action_type": log.action_type,
            "resource_type": log.resource_type,
            "resource_id": log.resource_id,
            "request_data": log.request_data,
            "response_data": log.response_data,
            "status": log.status,
            "error_message": log.error_message,
            "latency_ms": log.latency_ms,
            "extra_info": log.extra_info,
            "timestamp": log.timestamp,
        }
