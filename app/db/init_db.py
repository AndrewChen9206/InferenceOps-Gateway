from app.db.seed import seed_database
from app.db.session import AsyncSessionLocal


async def init_db() -> None:
    async with AsyncSessionLocal() as session:
        await seed_database(session)
