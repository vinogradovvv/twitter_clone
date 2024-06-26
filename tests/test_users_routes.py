import pytest
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from app.db.db_models import Users


@pytest.mark.asyncio(scope="session")
async def test_users_me_ok(test_client, test_session):
    user = (await test_session.execute(select(Users))).scalars().first()
    response = await test_client.get(
        "/users/me", headers={"api-key": f"{user.api_key}"}
    )

    assert response.status_code == 200
    assert response.json()["result"]
    assert response.json()["user"]["name"] == user.name
    assert response.json()["user"]["id"] == user.id


@pytest.mark.asyncio(scope="session")
async def test_users_me_fail(test_client, test_session):
    response = await test_client.get("/users/me", headers={})
    assert response.status_code == 422
    assert not response.json()["result"]

    response = await test_client.get("/users/me", headers={"api-key": "46"})
    assert response.status_code == 401
    assert not response.json()["result"]


@pytest.mark.asyncio(scope="session")
async def test_users_id_ok(test_client, test_session):
    user = (await test_session.execute(select(Users))).scalars().first()
    other_user = (
        (await test_session.execute(select(Users).order_by(Users.id.desc())))
        .scalars()
        .first()
    )
    response = await test_client.get(
        f"/users/{other_user.id}", headers={"api-key": f"{user.api_key}"}
    )

    assert response.status_code == 200
    assert response.json()["result"]
    assert response.json()["user"]["name"] == other_user.name
    assert response.json()["user"]["id"] == other_user.id


@pytest.mark.asyncio(scope="session")
async def test_users_id_fail(test_client, test_session):
    # user = (await test_session.execute(select(Users))).scalars().first()
    user = (
        (
            await test_session.execute(
                select(Users).options(
                    selectinload(Users.followers), selectinload(Users.following)
                )
            )
        )
        .scalars()
        .first()
    )

    response = await test_client.get("/users/46", headers={})
    assert response.status_code == 422
    assert not response.json()["result"]

    response = await test_client.get("/users/46", headers={"api-key": "not_existing"})
    assert response.status_code == 401
    assert not response.json()["result"]

    response = await test_client.get(
        "/users/46", headers={"api-key": f"{user.api_key}"}
    )
    assert response.status_code == 404
    assert not response.json()["result"]

    response = await test_client.get(
        "/users/not_int", headers={"api-key": f"{user.api_key}"}
    )
    assert response.status_code == 422
    assert not response.json()["result"]


@pytest.mark.asyncio(scope="session")
async def test_users_id_follow_ok(test_client, test_session):
    user = (
        (
            await test_session.execute(
                select(Users).options(
                    selectinload(Users.followers), selectinload(Users.following)
                )
            )
        )
        .scalars()
        .first()
    )
    other_user = (
        (
            await test_session.execute(
                select(Users)
                .options(selectinload(Users.followers), selectinload(Users.following))
                .order_by(Users.id.desc())
            )
        )
        .scalars()
        .first()
    )

    assert user not in other_user.followers
    assert other_user not in user.following

    response = await test_client.post(
        f"/users/{other_user.id}/follow", headers={"api-key": f"{user.api_key}"}
    )

    await test_session.refresh(user)
    await test_session.refresh(other_user)

    assert response.status_code == 201
    assert response.json()["result"]
    assert user in other_user.followers
    assert other_user in user.following


@pytest.mark.asyncio(scope="session")
async def test_users_id_follow_fail(test_client, test_session):
    user = (
        (
            await test_session.execute(
                select(Users).options(
                    selectinload(Users.followers), selectinload(Users.following)
                )
            )
        )
        .scalars()
        .first()
    )
    other_user = (
        (
            await test_session.execute(
                select(Users)
                .options(selectinload(Users.followers), selectinload(Users.following))
                .order_by(Users.id.desc())
            )
        )
        .scalars()
        .first()
    )

    response = await test_client.post("/users/46/follow", headers={})
    assert response.status_code == 422
    assert not response.json()["result"]

    response = await test_client.post(
        "/users/46/follow", headers={"api-key": "not_existing"}
    )
    assert response.status_code == 401
    assert not response.json()["result"]

    response = await test_client.post(
        "/users/46/follow", headers={"api-key": f"{user.api_key}"}
    )
    assert response.status_code == 404
    assert not response.json()["result"]

    response = await test_client.post(
        f"/users/{other_user.id}/follow", headers={"api-key": f"{user.api_key}"}
    )
    assert response.status_code == 405
    assert not response.json()["result"]

    response = await test_client.post(
        "/users/not_int/follow", headers={"api-key": f"{user.api_key}"}
    )
    assert response.status_code == 422
    assert not response.json()["result"]


@pytest.mark.asyncio(scope="session")
async def test_users_id_unfollow_ok(test_client, test_session):
    user = (
        (
            await test_session.execute(
                select(Users).options(
                    selectinload(Users.followers), selectinload(Users.following)
                )
            )
        )
        .scalars()
        .first()
    )
    other_user = (
        (
            await test_session.execute(
                select(Users)
                .options(selectinload(Users.followers), selectinload(Users.following))
                .order_by(Users.id.desc())
            )
        )
        .scalars()
        .first()
    )

    assert user in other_user.followers
    assert other_user in user.following

    response = await test_client.delete(
        f"/users/{other_user.id}/follow", headers={"api-key": f"{user.api_key}"}
    )

    await test_session.refresh(user)
    await test_session.refresh(other_user)

    assert response.status_code == 200
    assert response.json()["result"]
    assert user not in other_user.followers
    assert other_user not in user.following


@pytest.mark.asyncio(scope="session")
async def test_users_id_unfollow_fail(test_client, test_session):
    user = (
        (
            await test_session.execute(
                select(Users).options(
                    selectinload(Users.followers), selectinload(Users.following)
                )
            )
        )
        .scalars()
        .first()
    )
    other_user = (
        (
            await test_session.execute(
                select(Users)
                .options(selectinload(Users.followers), selectinload(Users.following))
                .order_by(Users.id.desc())
            )
        )
        .scalars()
        .first()
    )

    response = await test_client.delete("/users/46/follow", headers={})
    assert response.status_code == 422
    assert not response.json()["result"]

    response = await test_client.delete(
        "/users/46/follow", headers={"api-key": "not_existing"}
    )
    assert response.status_code == 401
    assert not response.json()["result"]

    response = await test_client.delete(
        "/users/46/follow", headers={"api-key": f"{user.api_key}"}
    )
    assert response.status_code == 404
    assert not response.json()["result"]

    response = await test_client.delete(
        f"/users/{other_user.id}/follow", headers={"api-key": f"{user.api_key}"}
    )
    assert response.status_code == 405
    assert not response.json()["result"]

    response = await test_client.delete(
        "/users/not_int/follow", headers={"api-key": f"{user.api_key}"}
    )
    assert response.status_code == 422
    assert not response.json()["result"]
