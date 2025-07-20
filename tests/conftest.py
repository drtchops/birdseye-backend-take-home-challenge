import os
from collections.abc import AsyncGenerator, Generator

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import text
from sqlalchemy.exc import ProgrammingError
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlmodel import SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel.pool import StaticPool

from core.api import app
from core.config import Settings, get_settings
from core.db import get_session
from shortlinks.models import Shortlink


@pytest.fixture(autouse=True, scope="session")
def test_settings() -> Settings:
    settings = get_settings()
    os.environ["DATABASE_URL"] = f"{settings.database_url}_test"
    os.environ["SERVICE_ROOT"] = "http://test"
    settings.__init__()
    return settings


@pytest.fixture(scope="session")
def anyio_backend() -> str:
    """The supported async backends to test"""
    return "asyncio"


@pytest.fixture(autouse=True, scope="session")
async def db_models(test_settings: Settings) -> None:
    url, db_name = test_settings.database_url.rsplit("/", maxsplit=1)
    base_engine = create_async_engine(f"{url}/postgres")
    async with base_engine.connect() as conn:
        await conn.execution_options(isolation_level="AUTOCOMMIT")
        try:
            await conn.execute(text(f"DROP DATABASE {db_name};"))
        except ProgrammingError:
            pass
        await conn.execute(text(f"CREATE DATABASE {db_name};"))


@pytest.fixture()
async def session(test_settings: Settings) -> AsyncGenerator[AsyncSession]:
    """An async session to a test database"""
    engine = create_async_engine(test_settings.database_url, poolclass=StaticPool)
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
    async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with async_session() as session:
        yield session
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.drop_all)


@pytest.fixture()
def client(session: AsyncSession) -> Generator[AsyncClient]:
    """An async test client"""

    def get_session_override() -> AsyncSession:
        return session

    app.dependency_overrides[get_session] = get_session_override
    client = AsyncClient(transport=ASGITransport(app=app), base_url="http://test")
    yield client
    del app.dependency_overrides[get_session]


@pytest.fixture()
async def shortlink(session: AsyncSession) -> Shortlink:
    shortlink = Shortlink(long_url="https://www.example.com/very/long/url")
    session.add(shortlink)
    await session.commit()
    return shortlink


@pytest.fixture()
async def shortlink_list(session: AsyncSession) -> list[Shortlink]:
    shortlinks: list[Shortlink] = []
    for i in range(100):
        shortlink = Shortlink(long_url=f"https://www.example.com/very/long/url/{i}")
        session.add(shortlink)
        shortlinks.append(shortlink)
    await session.commit()
    return shortlinks
