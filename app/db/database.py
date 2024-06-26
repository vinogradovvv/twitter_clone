import os
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.orm import declarative_base

DB_HOST = os.getenv("POSTGRES_HOST")
DB_USER = os.getenv("POSTGRES_USER")
DB_PASS = os.getenv("POSTGRES_PASSWORD")
DB_NAME = os.getenv("POSTGRES_DB")
DB_URL = f"postgresql+asyncpg://{DB_USER}:{DB_PASS}@{DB_HOST}/{DB_NAME}"
engine = create_async_engine(DB_URL)
Base = declarative_base()
async_session = async_sessionmaker(bind=engine, expire_on_commit=False)
session = async_session()


async def get_session() -> AsyncGenerator:
    """
    Asynchronous session generator.
    :return: Asynchronous session.
    :rtype: AsyncGenerator
    """
    async with async_session() as session:
        yield session
