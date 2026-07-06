from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.db.models import ModelPrice, User


async def seed_default_user(session: AsyncSession) -> None:
    result = await session.execute(
        select(User).where(User.user_key == settings.default_user_key)
    )
    existing_user = result.scalar_one_or_none()

    if existing_user is not None:
        return

    user = User(
        user_key=settings.default_user_key,
        display_name="Andrew",
        daily_budget_usd=Decimal(str(settings.default_daily_budget_usd)),
        requests_per_minute=settings.default_requests_per_minute,
    )

    session.add(user)
    await session.commit()


async def seed_model_prices(session: AsyncSession) -> None:
    model_prices = [
        {
            "model_name": "cheap-model",
            "input_cost_per_1k_tokens": Decimal("0.0001"),
            "output_cost_per_1k_tokens": Decimal("0.0002"),
        },
        {
            "model_name": "premium-model",
            "input_cost_per_1k_tokens": Decimal("0.0020"),
            "output_cost_per_1k_tokens": Decimal("0.0060"),
        },
        {
            "model_name": "unstable-model",
            "input_cost_per_1k_tokens": Decimal("0.0010"),
            "output_cost_per_1k_tokens": Decimal("0.0030"),
        },
    ]

    for price_data in model_prices:
        result = await session.execute(
            select(ModelPrice).where(ModelPrice.model_name == price_data["model_name"])
        )
        existing_price = result.scalar_one_or_none()

        if existing_price is not None:
            continue

        session.add(ModelPrice(**price_data))

    await session.commit()


async def seed_database(session: AsyncSession) -> None:
    await seed_default_user(session)
    await seed_model_prices(session)
