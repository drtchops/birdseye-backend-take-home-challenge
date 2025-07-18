from contextlib import asynccontextmanager

from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlmodel.ext.asyncio.session import AsyncSession

# ensure models are registered
from shortlinks import models as shortlinks_models  # noqa: F401  # pyright: ignore[reportUnusedImport]
from stats import models as stats_models  # noqa: F401 # pyright: ignore[reportUnusedImport]

from .config import get_settings

settings = get_settings()
engine = create_async_engine(settings.database_url)


async def get_session():
    """Get a new async session for the configured database engine. To be used in a `with` block."""
    async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with async_session() as session:
        yield session


get_session_context = asynccontextmanager(get_session)
