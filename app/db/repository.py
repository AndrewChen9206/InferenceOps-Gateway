from decimal import Decimal
from datetime import UTC, datetime, time
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import ModelPrice, RequestLog, User


async def get_user_by_key(session: AsyncSession, user_key: str) -> User | None:
    result = await session.execute(select(User).where(User.user_key == user_key))
    return result.scalar_one_or_none()


async def get_model_price(session: AsyncSession, model_name: str) -> ModelPrice | None:
    result = await session.execute(
        select(ModelPrice).where(ModelPrice.model_name == model_name)
    )
    return result.scalar_one_or_none()


def to_naive_utc(dt: datetime) -> datetime:
    """Convert a datetime to naive UTC."""

    if dt.tzinfo is None:
        return dt

    return dt.astimezone(UTC).replace(tzinfo=None)


async def get_user_estimated_spend_today(
    session: AsyncSession,
    *,
    user_id: UUID,
    now: datetime | None = None,
) -> Decimal:
    current_time = to_naive_utc(now or datetime.now(UTC))

    start_of_day = datetime.combine(
        current_time.date(),
        time.min,
    )

    result = await session.execute(
        select(func.coalesce(func.sum(RequestLog.estimated_cost_usd), 0)).where(
            RequestLog.user_id == user_id,
            RequestLog.created_at >= start_of_day,
            RequestLog.status == "success",
        )
    )

    return Decimal(result.scalar_one())


async def create_request_log(
    session: AsyncSession,
    *,
    user_id: UUID,
    task_type: str,
    policy: str,
    selected_model: str,
    prompt_hash: str,
    estimated_input_tokens: int,
    estimated_output_tokens: int,
    estimated_cost_usd: Decimal,
    latency_ms: int,
    status: str,
    output_preview: str | None,
    cache_key: str | None = None,
    cache_hit: bool = False,
    fallback_used: bool = False,
    primary_model: str | None = None,
    fallback_model: str | None = None,
    error_type: str | None = None,
) -> RequestLog:
    request_log = RequestLog(
        user_id=user_id,
        task_type=task_type,
        policy=policy,
        selected_model=selected_model,
        prompt_hash=prompt_hash,
        cache_key=cache_key,
        cache_hit=cache_hit,
        fallback_used=fallback_used,
        primary_model=primary_model,
        fallback_model=fallback_model,
        estimated_input_tokens=estimated_input_tokens,
        estimated_output_tokens=estimated_output_tokens,
        estimated_cost_usd=estimated_cost_usd,
        latency_ms=latency_ms,
        status=status,
        error_type=error_type,
        output_preview=output_preview,
    )

    session.add(request_log)
    await session.commit()
    await session.refresh(request_log)

    return request_log
