from db.db_models import Users
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

TEST_USERS = [
    {"name": "Stan Marsh", "api_key": "test"},
    {"name": "Kyle Broflovski", "api_key": "test2"},
    {"name": "Eric Cartman", "api_key": "test3"},
    {"name": "Kenny McCormick", "api_key": "test4"},
]


async def init_db(session: AsyncSession) -> None:
    """
    Fills database with init data.
    :param session: Asynchronous session
    :type session: AsyncSession
    """
    res = await session.execute(select(Users))
    if not res.first():
        new_users = [Users(**user) for user in TEST_USERS]
        session.add_all(new_users)
        await session.commit()
