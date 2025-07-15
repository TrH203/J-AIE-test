from app.models.action_log import ActionLog
from app.core.database import get_session
from sqlalchemy.dialects.postgresql import insert
from loguru import logger
import traceback
from fastapi import Query, HTTPException
from sqlalchemy import select

async def log_action(
    action_type: str,
    resource_type: str,
    resource_id: str = None,
    request_data: dict = None,
    response_data: dict = None,
    status: str = "success",
    error_message: str = None,
    latency_ms: int = None,
    extra_info: dict = None
):
    async with get_session() as session:
        try:
            stmt = insert(ActionLog).values(
                action_type=action_type,
                resource_type=resource_type,
                resource_id=resource_id,
                request_data=request_data,
                response_data=response_data,
                status=status,
                error_message=error_message,
                latency_ms=latency_ms,
                extra_info=extra_info
            )
            await session.execute(stmt)
            await session.commit()
        except Exception as e:
            logger.error(f"Failed to log action: {e}\n{traceback.format_exc()}")

async def list_all_action_logs(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=500),
    action_type: str | None = None,
    resource_type: str | None = None
):
    async with get_session() as session:
        stmt = select(ActionLog).order_by(ActionLog.timestamp.desc())

        if action_type:
            stmt = stmt.where(ActionLog.action_type == action_type)
        if resource_type:
            stmt = stmt.where(ActionLog.resource_type == resource_type)

        stmt = stmt.offset(skip).limit(limit)
        result = await session.execute(stmt)
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
        
async def search_log_by_id(log_id: str):
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