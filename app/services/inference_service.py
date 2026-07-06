from decimal import Decimal

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.cost import estimate_cost_usd, estimate_input_tokens
from app.core.normalization import hash_text, normalize_prompt
from app.db.repository import create_request_log, get_model_price, get_user_by_key
from app.providers.mock_provider import MockProvider
from app.schemas.inference import InferRequest, InferResponse


async def run_inference(
    *,
    session: AsyncSession,
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

    request_log = await create_request_log(
        session,
        user_id=user.id,
        task_type=request.task_type.value,
        policy=request.policy.value,
        selected_model=selected_model,
        prompt_hash=prompt_hash,
        estimated_input_tokens=estimated_input_tokens,
        estimated_output_tokens=provider_response.estimated_output_tokens,
        estimated_cost_usd=estimated_cost,
        latency_ms=provider_response.latency_ms,
        status="success",
        output_preview=provider_response.output[:200],
        cache_hit=False,
        fallback_used=False,
        primary_model=selected_model,
    )

    return InferResponse(
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
        latency_ms=provider_response.latency_ms,
        policy=request.policy,
    )
