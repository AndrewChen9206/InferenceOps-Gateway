import json

from redis.asyncio import Redis

from app.core.normalization import hash_text
from app.schemas.inference import CachedInferenceResult


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


async def get_cached_response(
    redis: Redis,
    cache_key: str,
) -> CachedInferenceResult | None:
    cached_value = await redis.get(cache_key)

    if cached_value is None:
        return None

    return CachedInferenceResult.model_validate_json(cached_value)


async def set_cached_response(
    redis: Redis,
    *,
    cache_key: str,
    response_data: CachedInferenceResult,
    ttl_seconds: int,
) -> None:
    await redis.set(
        cache_key,
        response_data.model_dump_json(),
        ex=ttl_seconds,
    )
