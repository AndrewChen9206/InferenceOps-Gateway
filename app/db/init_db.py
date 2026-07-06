from app.db.models import Base
from app.db.seed import seed_database
from app.db.session import AsyncSessionLocal, engine


async def init_db() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with AsyncSessionLocal() as session:
        await seed_database(session)
