from datetime import UTC, datetime

from redis.asyncio import Redis


def build_rate_limit_key(user_id: str, now: datetime | None = None) -> str:
    current_time = now or datetime.now(UTC)
    window = current_time.strftime("%Y%m%d%H%M")
    return f"rate_limit:{user_id}:{window}"


async def check_rate_limit(
    redis: Redis,
    *,
    user_id: str,
    limit: int,
    window_seconds: int = 60,
) -> bool:
    key = build_rate_limit_key(user_id)
    current_count = await redis.incr(key)

    if current_count == 1:
        await redis.expire(key, window_seconds)

    return current_count <= limit
