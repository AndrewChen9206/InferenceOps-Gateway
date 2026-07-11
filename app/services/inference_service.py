import logging
from decimal import Decimal

from redis.asyncio import Redis
from redis.exceptions import RedisError
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.core.cache import (
    build_cache_key,
    build_raw_cache_key,
    get_cached_response,
    set_cached_response,
)
from app.core.errors import (
    BudgetExceededError,
    ModelPriceNotFoundError,
    RateLimitExceededError,
    UnknownUserError,
)
from app.db.repository import (
    create_request_log,
    get_model_price,
    get_user_by_key,
    get_user_estimated_spend_today,
)
from app.core.cost import (
    estimate_cost_usd,
    estimate_input_tokens,
    estimate_output_tokens,
)
from app.core.normalization import hash_text, normalize_prompt
from app.core.rate_limit import check_rate_limit
from app.core.timing import elapsed_ms, start_timer
from app.providers.mock_provider import MockProvider
from app.schemas.inference import (
    CachedInferenceResult,
    InferRequest,
    InferResponse,
)


logger = logging.getLogger(__name__)


async def run_inference(
    *,
    session: AsyncSession,
    redis: Redis,
    request: InferRequest,
) -> InferResponse:
    started_at = start_timer()

    user = await get_user_by_key(session, request.user_id)
    if user is None:
        raise UnknownUserError(request.user_id)

    allowed = await check_rate_limit(
        redis,
        user_id=request.user_id,
        limit=user.requests_per_minute,
    )

    if not allowed:
        raise RateLimitExceededError(
            user_id=request.user_id,
            limit=user.requests_per_minute,
        )

    provider = MockProvider()
    selected_model = provider.model_name

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
            cache_hit_cost = Decimal("0")
            cache_hit_latency_ms = elapsed_ms(started_at)

            request_log = await create_request_log(
                session,
                user_id=user.id,
                task_type=request.task_type.value,
                policy=request.policy.value,
                selected_model=cached_response.selected_model,
                prompt_hash=prompt_hash,
                cache_key=cache_key,
                cache_hit=True,
                fallback_used=False,
                primary_model=cached_response.selected_model,
                estimated_input_tokens=cached_response.estimated_input_tokens,
                estimated_output_tokens=cached_response.estimated_output_tokens,
                estimated_cost_usd=cache_hit_cost,
                latency_ms=cache_hit_latency_ms,
                status="success",
                output_preview=cached_response.output[:200],
            )

            return InferResponse(
                request_id=str(request_log.id),
                user_id=request.user_id,
                task_type=request.task_type,
                selected_model=cached_response.selected_model,
                output=cached_response.output,
                cache_hit=True,
                fallback_used=False,
                estimated_input_tokens=cached_response.estimated_input_tokens,
                estimated_output_tokens=cached_response.estimated_output_tokens,
                estimated_cost_usd=float(cache_hit_cost),
                latency_ms=cache_hit_latency_ms,
                policy=request.policy,
            )

    model_price = await get_model_price(session, selected_model)
    if model_price is None:
        raise ModelPriceNotFoundError(selected_model)

    estimated_input_tokens = estimate_input_tokens(normalized_prompt)
    precheck_output_tokens = estimate_output_tokens(request.max_tokens)

    estimated_precheck_cost = estimate_cost_usd(
        input_tokens=estimated_input_tokens,
        output_tokens=precheck_output_tokens,
        input_cost_per_1k_tokens=Decimal(model_price.input_cost_per_1k_tokens),
        output_cost_per_1k_tokens=Decimal(model_price.output_cost_per_1k_tokens),
    )

    current_spend = await get_user_estimated_spend_today(
        session,
        user_id=user.id,
    )

    projected_spend = current_spend + estimated_precheck_cost

    if projected_spend > Decimal(user.daily_budget_usd):
        raise BudgetExceededError(
            user_id=request.user_id,
            budget_usd=str(user.daily_budget_usd),
            projected_spend_usd=str(projected_spend),
        )

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

    gateway_latency_ms = elapsed_ms(started_at)

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
        latency_ms=gateway_latency_ms,
        status="success",
        output_preview=provider_response.output[:200],
    )

    response = InferResponse(
        request_id=str(request_log.id),
        user_id=request.user_id,
        task_type=request.task_type,
        selected_model=selected_model,
        output=provider_response.output,
        cache_hit=False,
        fallback_used=False,
        estimated_input_tokens=estimated_input_tokens,
        estimated_output_tokens=provider_response.estimated_output_tokens,
        estimated_cost_usd=float(estimated_cost),
        latency_ms=gateway_latency_ms,
        policy=request.policy,
    )

    if request.cache:
        cached_result = CachedInferenceResult(
            selected_model=selected_model,
            output=provider_response.output,
            estimated_input_tokens=estimated_input_tokens,
            estimated_output_tokens=provider_response.estimated_output_tokens,
        )

        try:
            await set_cached_response(
                redis,
                cache_key=cache_key,
                response_data=cached_result,
                ttl_seconds=settings.default_cache_ttl_seconds,
            )
        except RedisError:
            logger.warning(
                "Failed to cache inference response",
                extra={
                    "request_id": str(request_log.id),
                    "cache_key": cache_key,
                    "selected_model": selected_model,
                },
                exc_info=True,
            )

    return response
