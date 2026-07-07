from decimal import Decimal

from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.core.cache import (
    build_cache_key,
    build_raw_cache_key,
    get_cached_response,
    set_cached_response,
)
from app.core.cost import estimate_cost_usd, estimate_input_tokens
from app.core.normalization import hash_text, normalize_prompt
from app.db.repository import create_request_log, get_model_price, get_user_by_key
from app.providers.mock_provider import MockProvider
from app.schemas.inference import InferRequest, InferResponse


async def run_inference(
    *,
    session: AsyncSession,
    redis: Redis,
    request: InferRequest,
) -> InferResponse:
    user = await get_user_by_key(session, request.user_id)
    if user is None:
        raise ValueError(f"Unknown user_id: {request.user_id}")

    provider = MockProvider()
    selected_model = provider.model_name

    model_price = await get_model_price(session, selected_model)
    if model_price is None:
        raise ValueError(f"Missing model price for model: {selected_model}")

    normalized_prompt = normalize_prompt(request.prompt)
    prompt_hash = hash_text(normalized_prompt)

    raw_cache_key = build_raw_cache_key(
        task_type=request.task_type.value,
        selected_model=selected_model,
        normalized_prompt=normalized_prompt,
        temperature=request.temperature,
        max_tokens=request.max_tokens,
        cache_key_version=settings.cache_key_version,
        prompt_template_version=settings.prompt_template_version,
        model_version=settings.model_version,
    )
    cache_key = build_cache_key(raw_cache_key)

    if request.cache:
        cached_response = await get_cached_response(redis, cache_key)
        if cached_response is not None:
            request_log = await create_request_log(
                session,
                user_id=user.id,
                task_type=request.task_type.value,
                policy=request.policy.value,
                selected_model=selected_model,
                prompt_hash=prompt_hash,
                cache_key=cache_key,
                cache_hit=True,
                fallback_used=False,
                primary_model=selected_model,
                estimated_input_tokens=cached_response["estimated_input_tokens"],
                estimated_output_tokens=cached_response["estimated_output_tokens"],
                estimated_cost_usd=Decimal(str(cached_response["estimated_cost_usd"])),
                latency_ms=0,
                status="success",
                output_preview=cached_response["output"][:200],
            )

            return InferResponse(
                request_id=str(request_log.id),
                user_id=request.user_id,
                task_type=request.task_type,
                selected_model=selected_model,
                output=cached_response["output"],
                cache_hit=True,
                fallback_used=False,
                estimated_input_tokens=cached_response["estimated_input_tokens"],
                estimated_output_tokens=cached_response["estimated_output_tokens"],
                estimated_cost_usd=cached_response["estimated_cost_usd"],
                latency_ms=0,
                policy=request.policy,
            )

    estimated_input_tokens = estimate_input_tokens(normalized_prompt)

    provider_response = await provider.generate(
        task_type=request.task_type.value,
        prompt=normalized_prompt,
        max_tokens=request.max_tokens,
        temperature=request.temperature,
    )

    estimated_cost = estimate_cost_usd(
        input_tokens=estimated_input_tokens,
        output_tokens=provider_response.estimated_output_tokens,
        input_cost_per_1k_tokens=Decimal(model_price.input_cost_per_1k_tokens),
        output_cost_per_1k_tokens=Decimal(model_price.output_cost_per_1k_tokens),
    )

    response = InferResponse(
        request_id="pending",
        user_id=request.user_id,
        task_type=request.task_type,
        selected_model=selected_model,
        output=provider_response.output,
        cache_hit=False,
        fallback_used=False,
        estimated_input_tokens=estimated_input_tokens,
        estimated_output_tokens=provider_response.estimated_output_tokens,
        estimated_cost_usd=float(estimated_cost),
        latency_ms=provider_response.latency_ms,
        policy=request.policy,
    )

    if request.cache:
        await set_cached_response(
            redis,
            cache_key=cache_key,
            response_data=response.model_dump(mode="json", exclude={"request_id"}),
            ttl_seconds=settings.default_cache_ttl_seconds,
        )

    request_log = await create_request_log(
        session,
        user_id=user.id,
        task_type=request.task_type.value,
        policy=request.policy.value,
        selected_model=selected_model,
        prompt_hash=prompt_hash,
        cache_key=cache_key if request.cache else None,
        cache_hit=False,
        fallback_used=False,
        primary_model=selected_model,
        estimated_input_tokens=estimated_input_tokens,
        estimated_output_tokens=provider_response.estimated_output_tokens,
        estimated_cost_usd=estimated_cost,
        latency_ms=provider_response.latency_ms,
        status="success",
        output_preview=provider_response.output[:200],
    )

    response.request_id = str(request_log.id)
    return response
