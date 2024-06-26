import os
from typing import AsyncGenerator

import pytest
from dotenv import load_dotenv
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.db.database import get_session
from app.db.db_models import Base
from app.init_db import init_db
from app.main import app

load_dotenv('envs/dev.env', override=True)
DB_HOST = os.getenv('POSTGRES_HOST')
DB_USER = os.getenv('POSTGRES_USER')
DB_PASS = os.getenv('POSTGRES_PASSWORD')
DB_NAME = os.getenv('POSTGRES_DB')

TEST_DATABASE_URL = (
    f"postgresql+asyncpg://{DB_USER}:{DB_PASS}@{DB_HOST}/{DB_NAME}"
)

test_engine = create_async_engine(TEST_DATABASE_URL)
test_async_session = async_sessionmaker(bind=test_engine, expire_on_commit=False)
test_async_client = AsyncClient(
    transport=ASGITransport(app=app),  # type: ignore[arg-type]
    base_url="http://localhost/api"
)


async def override_get_session() -> AsyncGenerator:
    """
    Test database session generator
    :return: Asynchronous session
    :rtype: AsyncSession
    """
    async with test_async_session() as session:
        yield session


app.dependency_overrides[get_session] = override_get_session


@pytest.fixture(autouse=True, scope="session")
async def create_test_db():
    """
    Creates tables in test database and fills them with test data.
    """
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    async with test_async_session() as session:
        await init_db(session=session)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await test_engine.dispose()


@pytest.fixture(scope="session")
async def test_client():
    """
    Provides test client.
    """
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://localhost/api"
    ) as test_client:
        yield test_client


@pytest.fixture(scope="session")
async def test_session():
    """
    Provides test session.
    """
    async with test_async_session() as test_session:
        yield test_session
