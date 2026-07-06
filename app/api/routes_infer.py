from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import AsyncSessionLocal
from app.schemas.inference import InferRequest, InferResponse
from app.services.inference_service import run_inference


router = APIRouter(prefix="/v1", tags=["inference"])


async def get_db_session():
    async with AsyncSessionLocal() as session:
        yield session


@router.post("/infer", response_model=InferResponse)
async def infer(
    request: InferRequest,
    session: AsyncSession = Depends(get_db_session),
) -> InferResponse:
    try:
        return await run_inference(session=session, request=request)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc
