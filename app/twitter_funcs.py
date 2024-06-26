from collections.abc import Callable
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession
from twitter_exception import TwitterWrongApiKeyException


async def check_api_key(
    api_key: str, get_user_method: Callable, session: AsyncSession
) -> tuple[str, Any]:
    """

    :param api_key: Api key header.
    :type api_key: str
    :param get_user_method: Method to get user with given api key.
    :type get_user_method: Callable
    :param session: Asynchronous session
    :type session: AsyncSession
    :return: api key and user data
    :rtype: tuple[str, Any]
    """

    user = await get_user_method(session=session, api_key=api_key)
    if not user:
        raise TwitterWrongApiKeyException
    return user
