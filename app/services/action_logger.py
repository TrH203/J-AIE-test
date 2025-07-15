from app.models.action_log import ActionLog
from app.core.database import get_session
from sqlalchemy.dialects.postgresql import insert
from loguru import logger
import traceback

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
