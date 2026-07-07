from fastapi import APIRouter, Depends, HTTPException, status
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_db_session, get_redis_client
from app.schemas.inference import InferRequest, InferResponse
from app.services.inference_service import run_inference


router = APIRouter(prefix="/v1", tags=["inference"])


@router.post("/infer", response_model=InferResponse)
async def infer(
    request: InferRequest,
    session: AsyncSession = Depends(get_db_session),
    redis: Redis = Depends(get_redis_client),
) -> InferResponse:
    try:
        return await run_inference(session=session, redis=redis, request=request)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc
