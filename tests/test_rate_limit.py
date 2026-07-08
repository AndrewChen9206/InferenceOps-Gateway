from datetime import UTC, datetime

import pytest
from redis.asyncio import Redis

from app.config import settings
from app.core.rate_limit import build_rate_limit_key, check_rate_limit


def test_build_rate_limit_key_uses_user_and_minute() -> None:
    now = datetime(2026, 7, 8, 14, 30, tzinfo=UTC)

    key = build_rate_limit_key("andrew", now=now)

    assert key == "rate_limit:andrew:202607081430"


@pytest.mark.asyncio
async def test_check_rate_limit_allows_requests_within_limit() -> None:
    redis = Redis.from_url(settings.redis_url, decode_responses=True)

    try:
        first_allowed = await check_rate_limit(
            redis,
            user_id="rate-limit-test-user",
            limit=2,
        )
        second_allowed = await check_rate_limit(
            redis,
            user_id="rate-limit-test-user",
            limit=2,
        )

        assert first_allowed is True
        assert second_allowed is True
    finally:
        await redis.aclose()


@pytest.mark.asyncio
async def test_check_rate_limit_rejects_requests_over_limit() -> None:
    redis = Redis.from_url(settings.redis_url, decode_responses=True)

    try:
        first_allowed = await check_rate_limit(
            redis,
            user_id="rate-limit-test-user",
            limit=1,
        )
        second_allowed = await check_rate_limit(
            redis,
            user_id="rate-limit-test-user",
            limit=1,
        )

        assert first_allowed is True
        assert second_allowed is False
    finally:
        await redis.aclose()
