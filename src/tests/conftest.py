import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlmodel import SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel.pool import StaticPool

from src.api import app
from src.db import get_session


@pytest.fixture()
def anyio_backend():
    """The supported async backends to test"""
    return "asyncio"


@pytest.fixture()
async def session():
    """An async session to a test database"""
    engine = create_async_engine("sqlite+aiosqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
    async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with async_session() as session:
        yield session


@pytest.fixture()
def client(session: AsyncSession):
    """An async test client"""

    def get_session_override() -> AsyncSession:
        return session

    app.dependency_overrides[get_session] = get_session_override
    client = AsyncClient(transport=ASGITransport(app=app), base_url="http://test")
    yield client
    del app.dependency_overrides[get_session]
