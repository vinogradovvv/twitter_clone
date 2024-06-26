import os
import shutil

import pytest
from sqlalchemy import func
from sqlalchemy.future import select

from app.db.db_models import Media, Users


@pytest.mark.asyncio(scope="session")
async def test_add_media_ok(test_client, test_session):
    # tmp_path = "./media"
    tmp_path = os.getenv('MEDIA_PATH')
    if not os.path.exists(tmp_path):
        os.makedirs(tmp_path)

    user = (await test_session.execute(select(Users))).scalars().first()
    images_number = (
        await test_session.execute(select(func.count()).select_from(Media))
    ).scalar()
    files = {"file": open("tests/test_image.jpg", "rb")}
    response = await test_client.post(
        "/medias", files=files, headers={"api-key": f"{user.api_key}"}
    )
    new_images_number = (
        await test_session.execute(select(func.count()).select_from(Media))
    ).scalar()
    print(response.json())
    assert response.status_code == 201
    assert response.json()["result"]
    assert "media_id" in response.json()
    assert new_images_number - images_number == 1

    shutil.rmtree(tmp_path)


@pytest.mark.asyncio(scope="session")
async def test_add_media_fail(test_client, test_session):
    user = (await test_session.execute(select(Users))).scalars().first()
    files = {"file": open("tests/test_image.jpg", "rb")}

    response = await test_client.post("/medias", files=files, headers={})
    assert response.status_code == 422
    assert not response.json()["result"]

    response = await test_client.post(
        "/medias", files={}, headers={"api-key": f"{user.api_key}"}
    )
    assert response.status_code == 422
    assert not response.json()["result"]

    response = await test_client.post("/medias", files=files, headers={"api-key": "46"})
    assert response.status_code == 401
    assert not response.json()["result"]
