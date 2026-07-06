from fastapi import APIRouter
from redis.asyncio import Redis
from sqlalchemy import text

from app.config import settings
from app.db.session import AsyncSessionLocal


router = APIRouter()


@router.get("/healthz")
async def healthz() -> dict[str, str]:
    return {"status": "ok"}


@router.get("/readyz")
async def readyz() -> dict[str, str]:
    async with AsyncSessionLocal() as session:
        await session.execute(text("SELECT 1"))

    redis = Redis.from_url(settings.redis_url, decode_responses=True)
    await redis.ping()
    await redis.aclose()

    return {
        "status": "ready",
        "postgres": "ok",
        "redis": "ok",
    }
