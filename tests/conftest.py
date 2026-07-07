import pytest
from fastapi.testclient import TestClient
from redis import Redis

from app.config import settings
from app.main import app


@pytest.fixture(autouse=True)
def clear_redis_cache() -> None:
    redis = Redis.from_url(settings.redis_url, decode_responses=True)
    redis.flushdb()
    redis.close()


@pytest.fixture(scope="session")
def client():
    with TestClient(app) as test_client:
        yield test_client
