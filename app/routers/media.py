import os
from typing import Annotated, Dict

import aiofiles
from fastapi import APIRouter, Depends, Header, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

import app.db.db_models as db_models
import app.schemas as schemas
from app.db.database import get_session
from app.twitter_exception import TwitterNoFileException
from app.twitter_funcs import check_api_key

router = APIRouter(
    prefix="/api/medias", tags=["medias"], dependencies=[Depends(get_session)]
)


@router.post(
    "",
    response_model=schemas.AddMediaResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        400: {"model": schemas.FailResponse},
        401: {"model": schemas.FailResponse},
        422: {"model": schemas.FailResponse},
    },
)
async def upload_media(
    api_key: Annotated[str, Header()],
    file: UploadFile,
    session: AsyncSession = Depends(get_session),
) -> Dict[str, bool | int]:
    """

    :param api_key: Api key header.
    :type api_key: str
    :param file: Uploaded file.
    :type file: UploadFile
    :param session: Asynchronous session.
    :type session: AsyncSession
    :return: Response
    :rtype: Dict[str, bool | int]
    """
    if not file:
        raise TwitterNoFileException
    await check_api_key(api_key, db_models.Users.get_user_by_api_key, session)
    new_id = await db_models.Tweets.get_new_id(session)
    name = f"{str(new_id)}__{file.filename}"
    path = os.getenv("MEDIA_PATH")
    async with aiofiles.open(
            "".join((path, name)),  # type: ignore[arg-type, call-overload]
            "wb") as new_file:
        await new_file.write(file.file.read())
    new_media = db_models.Media(**{"filename": name})
    session.add(new_media)
    await session.commit()
    return {"result": True, "media_id": int(new_media.id)}
