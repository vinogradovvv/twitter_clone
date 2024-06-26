import os
from typing import Annotated, Dict, List, Optional, Sequence

from fastapi import APIRouter, Body, Depends, Header, Path, status
from sqlalchemy import desc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

import app.db.db_models as db_models
import app.schemas as schemas
from app.db.database import get_session
from app.twitter_exception import (
    TwitterAlreadyLikedException,
    TwitterDidNotLikeException,
    TwitterNoMediaException,
    TwitterNoTweetException,
    TwitterOwnerException,
)
from app.twitter_funcs import check_api_key

PATH = "./media/"

router = APIRouter(
    prefix="/api/tweets", tags=["tweets"], dependencies=[Depends(get_session)]
)


@router.post(
    "",
    response_model=schemas.AddTweetResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        401: {"model": schemas.FailResponse},
        404: {"model": schemas.FailResponse},
        422: {"model": schemas.FailResponse},
    },
)
async def add_tweet(
    api_key: Annotated[str, Header()],
    tweet_data: Annotated[str, Body()],
    tweet_media_ids: Annotated[Optional[List[int]], Body()] = None,
    session: AsyncSession = Depends(get_session),
) -> Dict[str, bool | int]:
    """
    Endpoint to add new tweet.
    :param api_key: Api key header.
    :type api_key: str
    :param session: Asynchronous session.
    :type session: AsyncSession
    :param tweet_data: Tweet data.
    :type tweet_data: str
    :param tweet_media_ids: Id of uploaded media.
    :type tweet_media_ids: Optional[List[int]]
    :return: Response
    :rtype: Dict[str, bool | int]
    """
    user = await check_api_key(api_key, db_models.Users.get_user_by_api_key, session)
    new_tweet = db_models.Tweets(
        **{
            "content": tweet_data,
            "author_id": int(user.id),  # type: ignore[attr-defined]
        }
    )
    if tweet_media_ids:
        attachments = []
        for media_id in tweet_media_ids:
            media = await db_models.Media.get_media_by_id(session=session, id=media_id)
            if not media:
                raise TwitterNoMediaException
            attachments.append(media)
        new_tweet.media = attachments
    session.add(new_tweet)
    await session.commit()
    return {"result": True, "tweet_id": int(new_tweet.id)}


@router.delete(
    "/{id}",
    response_model=schemas.ResultResponse,
    status_code=status.HTTP_200_OK,
    responses={
        401: {"model": schemas.FailResponse},
        404: {"model": schemas.FailResponse},
        405: {"model": schemas.FailResponse},
        422: {"model": schemas.FailResponse},
    },
)
async def delete_tweet(
    api_key: Annotated[str, Header()],
    id: Annotated[int, Path()],
    session: AsyncSession = Depends(get_session),
) -> Dict[str, bool]:
    """
    Endpoint to delete tweet with given id.
    :param api_key: Api key header.
    :type api_key: str
    :param id: Tweet id
    :type id: int
    :param session: Asynchronous session.
    :type session: AsyncSession
    :return: Response
    :rtype: Dict[str, bool]
    """
    user = await check_api_key(api_key, db_models.Users.get_user_by_api_key, session)
    tweet = await db_models.Tweets.get_tweet_by_id(session=session, id=id)
    if not tweet:
        raise TwitterNoTweetException
    if tweet.author_id != user.id:  # type: ignore[attr-defined]
        raise TwitterOwnerException
    for media in tweet.attachments:
        os.remove("".join((PATH, media)))
    await session.delete(tweet)
    await session.commit()
    return {"result": True}


@router.post(
    "/{id}/likes",
    response_model=schemas.ResultResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        401: {"model": schemas.FailResponse},
        404: {"model": schemas.FailResponse},
        405: {"model": schemas.FailResponse},
        422: {"model": schemas.FailResponse},
    },
)
async def like_the_tweet(
    api_key: Annotated[str, Header()],
    id: Annotated[int, Path()],
    session: AsyncSession = Depends(get_session),
) -> Dict[str, bool]:
    """
    Endpoint to like tweet with given id.
    :param api_key: Api key header.
    :type api_key: str
    :param id: Tweet id
    :type id: int
    :param session: Asynchronous session.
    :type session: AsyncSession
    :return: Response
    :rtype: Dict[str, bool]
    """
    user = await check_api_key(api_key, db_models.Users.get_user_by_api_key, session)
    tweet = await db_models.Tweets.get_tweet_by_id(session=session, id=id)
    if not tweet:
        raise TwitterNoTweetException
    if user in tweet.likes:
        raise TwitterAlreadyLikedException
    tweet.likes.append(user)
    await session.commit()
    return {"result": True}


@router.delete(
    "/{id}/likes",
    response_model=schemas.ResultResponse,
    status_code=status.HTTP_200_OK,
    responses={
        401: {"model": schemas.FailResponse},
        404: {"model": schemas.FailResponse},
        405: {"model": schemas.FailResponse},
        422: {"model": schemas.FailResponse},
    },
)
async def unlike_the_tweet(
    api_key: Annotated[str, Header()],
    id: Annotated[int, Path()],
    session: AsyncSession = Depends(get_session),
) -> Dict[str, bool]:
    """
    Endpoint to unlike tweet with given id.
    :param api_key: Api key header.
    :type api_key: str
    :param id: Tweet id
    :type id: int
    :param session: Asynchronous session.
    :type session: AsyncSession
    :return: Response
    :rtype: Dict[str, bool]
    """
    user = await check_api_key(api_key, db_models.Users.get_user_by_api_key, session)
    tweet = await db_models.Tweets.get_tweet_by_id(session=session, id=id)
    if not tweet:
        raise TwitterNoTweetException
    if user not in tweet.likes:
        raise TwitterDidNotLikeException
    tweet.likes.remove(user)
    await session.commit()
    return {"result": True}


@router.get(
    "",
    response_model=schemas.TweetsResponse,
    status_code=status.HTTP_200_OK,
    responses={401: {"model": schemas.FailResponse}},
)
async def get_tweets(
    api_key: Annotated[str, Header()], session: AsyncSession = Depends(get_session)
) -> Dict[str, bool | Sequence[db_models.Tweets]]:
    """
    Endpoint to get all tweets.
    :param api_key: Api key header.
    :type api_key: str
    :param session: Asynchronous session.
    :type session: AsyncSession
    :return: Response
    :rtype: Dict[str, bool | Result]
    """
    await check_api_key(api_key, db_models.Users.get_user_by_api_key, session)
    res = await session.execute(
        select(db_models.Tweets).options(
            selectinload(db_models.Tweets.media),
            selectinload(db_models.Tweets.author),
            selectinload(db_models.Tweets.likes),
        ).order_by(desc(db_models.Tweets.id))
    )
    tweets = res.scalars().all()
    return {"result": True, "tweets": tweets}
