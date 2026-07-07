import json
from typing import Any

from redis.asyncio import Redis

from app.core.normalization import hash_text


def build_raw_cache_key(
    *,
    task_type: str,
    selected_model: str,
    normalized_prompt: str,
    temperature: float,
    max_tokens: int,
    cache_key_version: str,
    prompt_template_version: str,
    model_version: str,
) -> str:
    return json.dumps(
        {
            "cache_key_version": cache_key_version,
            "task_type": task_type,
            "selected_model": selected_model,
            "normalized_prompt": normalized_prompt,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "prompt_template_version": prompt_template_version,
            "model_version": model_version,
        },
        sort_keys=True,
        separators=(",", ":"),
    )


def build_cache_key(raw_cache_key: str) -> str:
    return f"cache:infer:{hash_text(raw_cache_key)}"


async def get_cached_response(redis: Redis, cache_key: str) -> dict[str, Any] | None:
    cached_value = await redis.get(cache_key)
    if cached_value is None:
        return None

    return json.loads(cached_value)


async def set_cached_response(
    redis: Redis,
    *,
    cache_key: str,
    response_data: dict[str, Any],
    ttl_seconds: int,
) -> None:
    await redis.set(
        cache_key,
        json.dumps(response_data),
        ex=ttl_seconds,
    )
