from typing import Annotated, Any, Dict

from fastapi import APIRouter, Depends, Header, Path, status
from sqlalchemy.ext.asyncio import AsyncSession

from app import schemas
from app.db import db_models
from app.db.database import get_session
from app.twitter_exception import (
    TwitterAlreadyFollowingException,
    TwitterDoNotFollowingException,
    TwitterNoUserException,
)
from app.twitter_funcs import check_api_key

router = APIRouter(
    prefix="/api/users", tags=["users"], dependencies=[Depends(get_session)]
)


@router.get(
    "/me",
    response_model=schemas.UserResponse,
    status_code=status.HTTP_200_OK,
    responses={401: {"model": schemas.FailResponse}},
)
async def me(
    api_key: Annotated[str, Header()], session: AsyncSession = Depends(get_session)
) -> Dict[str, bool | str | tuple[str, Any]]:
    """
    Endpoint to get current user.
    :param api_key: Api key header.
    :type api_key: str
    :param session: Asynchronous session.
    :type session: AsyncSession
    :return: Response
    :rtype: Dict[str, bool | str | db_models.Users]
    """
    user = await check_api_key(api_key, db_models.Users.get_user_by_api_key, session)
    return {"result": True, "user": user}


@router.get(
    "/{id}",
    response_model=schemas.UserResponse,
    status_code=status.HTTP_200_OK,
    responses={
        401: {"model": schemas.FailResponse},
        404: {"model": schemas.FailResponse},
        422: {"model": schemas.FailResponse},
    },
)
async def user_by_id(
    api_key: Annotated[str, Header()],
    id: Annotated[int, Path()],
    session: AsyncSession = Depends(get_session),
) -> Dict[str, bool | str | db_models.Users]:
    """
    Endpoint to get user with given id.
    :param api_key: Api key header.
    :type api_key: str
    :param id: User id
    :type id: int
    :param session: Asynchronous session.
    :type session: AsyncSession
    :return: Response
    :rtype: Dict[str, bool | str | db_models.Users]
    """
    await check_api_key(api_key, db_models.Users.get_user_by_api_key, session)
    user = await db_models.Users.get_user_by_id(session=session, id=id)
    if not user:
        raise TwitterNoUserException
    return {"result": True, "user": user}


@router.post(
    "/{id}/follow",
    response_model=schemas.ResultResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        401: {"model": schemas.FailResponse},
        404: {"model": schemas.FailResponse},
        405: {"model": schemas.FailResponse},
        422: {"model": schemas.FailResponse},
    },
)
async def follow_user(
    api_key: Annotated[str, Header()],
    id: Annotated[int, Path()],
    session: AsyncSession = Depends(get_session),
) -> Dict[str, bool]:
    """
    Endpoint to follow user with given id.
    :param api_key: Api key header.
    :type api_key: str
    :param id: User id
    :type id: int
    :param session: Asynchronous session.
    :type session: AsyncSession
    :return: Response
    :rtype: Dict[str, bool]
    """
    follower = await check_api_key(
        api_key, db_models.Users.get_user_by_api_key, session
    )
    user = await db_models.Users.get_user_by_id(session=session, id=id)
    if not user:
        raise TwitterNoUserException
    if follower in user.followers:
        raise TwitterAlreadyFollowingException
    user.followers.append(follower)
    await session.commit()
    return {"result": True}


@router.delete(
    "/{id}/follow",
    response_model=schemas.ResultResponse,
    status_code=status.HTTP_200_OK,
    responses={
        401: {"model": schemas.FailResponse},
        404: {"model": schemas.FailResponse},
        405: {"model": schemas.FailResponse},
        422: {"model": schemas.FailResponse},
    },
)
async def unfollow_user(
    api_key: Annotated[str, Header()],
    id: Annotated[int, Path()],
    session: AsyncSession = Depends(get_session),
) -> Dict[str, bool]:
    """
    Endpoint to unfollow user with given id.
    :param api_key: Api key header.
    :type api_key: str
    :param id: User id
    :type id: int
    :param session: Asynchronous session.
    :type session: AsyncSession
    :return: Response
    :rtype: Dict[str, bool]
    """
    follower = await check_api_key(
        api_key, db_models.Users.get_user_by_api_key, session
    )
    user = await db_models.Users.get_user_by_id(session=session, id=id)
    if not user:
        raise TwitterNoUserException
    if follower not in user.followers:
        raise TwitterDoNotFollowingException
    user.followers.remove(follower)
    await session.commit()
    return {"result": True}
