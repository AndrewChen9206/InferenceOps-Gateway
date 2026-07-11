import logging

from fastapi import APIRouter, Depends, HTTPException, status
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.errors import (
    BudgetExceededError,
    ModelPriceNotFoundError,
    RateLimitExceededError,
    UnknownUserError,
)
from app.dependencies import get_db_session, get_redis_client
from app.schemas.inference import InferRequest, InferResponse
from app.services.inference_service import run_inference


logger = logging.getLogger(__name__)

router = APIRouter(prefix="/v1", tags=["inference"])


@router.post("/infer", response_model=InferResponse)
async def infer(
    request: InferRequest,
    session: AsyncSession = Depends(get_db_session),
    redis: Redis = Depends(get_redis_client),
) -> InferResponse:
    try:
        return await run_inference(
            session=session,
            redis=redis,
            request=request,
        )
    except RateLimitExceededError as exc:
        logger.warning(
            "Inference request rejected by rate limit",
            extra={
                "user_id": request.user_id,
                "task_type": request.task_type.value,
                "policy": request.policy.value,
                "limit": exc.limit,
                "error_type": "rate_limit_exceeded",
            },
        )

        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=str(exc),
        ) from exc

    except BudgetExceededError as exc:
        logger.warning(
            "Inference request rejected by daily budget",
            extra={
                "user_id": request.user_id,
                "task_type": request.task_type.value,
                "policy": request.policy.value,
                "budget_usd": exc.budget_usd,
                "projected_spend_usd": exc.projected_spend_usd,
                "error_type": "budget_exceeded",
            },
        )

        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail=str(exc),
        ) from exc

    except UnknownUserError as exc:
        logger.warning(
            "Inference request rejected for unknown user",
            extra={
                "user_id": request.user_id,
                "task_type": request.task_type.value,
                "policy": request.policy.value,
                "error_type": "unknown_user",
            },
        )

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc
    except ModelPriceNotFoundError as exc:
        logger.error(
            "Inference request failed because model pricing is missing",
            extra={
                "user_id": request.user_id,
                "task_type": request.task_type.value,
                "policy": request.policy.value,
                "model_name": exc.model_name,
                "error_type": "model_price_not_found",
            },
        )

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Inference service configuration error.",
        ) from exc
