import pytest
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from app.db.db_models import Tweets, Users


@pytest.mark.asyncio(scope="session")
async def test_add_tweet_ok(test_client, test_session):
    user = (await test_session.execute(select(Users))).scalars().first()
    request_data = {"tweet_data": "Test tweet message", "tweet_media_ids": []}

    response = await test_client.post(
        "/tweets", headers={"api-key": f"{user.api_key}"}, json=request_data
    )
    assert response.status_code == 201
    assert response.json()["result"]
    assert "tweet_id" in response.json()

    tweet = (
        (
            await test_session.execute(
                select(Tweets).filter(Tweets.id == response.json()["tweet_id"])
            )
        )
        .unique()
        .scalar_one_or_none()
    )
    assert tweet.id == response.json()["tweet_id"]
    assert tweet.content == request_data["tweet_data"]


@pytest.mark.asyncio(scope="session")
async def test_add_tweet_fail(test_client, test_session):
    user = (await test_session.execute(select(Users))).scalars().first()
    request_data = {"tweet_data": "Test tweet message", "tweet_media_ids": []}

    response = await test_client.post("/tweets", headers={}, json=request_data)
    assert response.status_code == 422
    assert not response.json()["result"]

    response = await test_client.post(
        "/tweets", headers={"api-key": "46"}, json=request_data
    )
    assert response.status_code == 401
    assert not response.json()["result"]

    response = await test_client.post("/tweets", headers={"api-key": f"{user.api_key}"})
    assert response.status_code == 422
    assert not response.json()["result"]


@pytest.mark.asyncio(scope="session")
async def test_delete_tweet_ok(test_client, test_session):
    user = (await test_session.execute(select(Users))).scalars().first()
    tweet_number = len(user.tweets)
    tweet_id = user.tweets[0].id

    response = await test_client.delete(
        f"/tweets/{tweet_id}", headers={"api-key": f"{user.api_key}"}
    )
    assert response.status_code == 200
    assert response.json()["result"]

    await test_session.refresh(user)
    new_tweet_number = len(user.tweets)
    assert tweet_number - new_tweet_number == 1


@pytest.mark.asyncio(scope="session")
async def test_delete_tweet_fail(test_client, test_session):
    await test_add_tweet_ok(test_client, test_session)
    user = (await test_session.execute(select(Users))).scalars().first()
    other_user = (
        (await test_session.execute(select(Users).order_by(Users.id.desc())))
        .scalars()
        .first()
    )
    tweet_id = user.tweets[0].id

    response = await test_client.delete(f"/tweets/{tweet_id}", headers={})
    assert response.status_code == 422
    assert not response.json()["result"]

    response = await test_client.delete(
        f"/tweets/{tweet_id}", headers={"api-key": "46"}
    )
    assert response.status_code == 401
    assert not response.json()["result"]

    response = await test_client.delete(
        "/tweets/46", headers={"api-key": f"{user.api_key}"}
    )
    assert response.status_code == 404
    assert not response.json()["result"]

    response = await test_client.delete(
        f"/tweets/{tweet_id}", headers={"api-key": f"{other_user.api_key}"}
    )
    assert response.status_code == 405
    assert not response.json()["result"]

    response = await test_client.delete(
        "/tweets/not_int", headers={"api-key": f"{user.api_key}"}
    )
    assert response.status_code == 422
    assert not response.json()["result"]


@pytest.mark.asyncio(scope="session")
async def test_like_tweet_ok(test_client, test_session):
    user = (await test_session.execute(select(Users))).scalars().first()
    tweet_id = user.tweets[0].id
    tweet = (
        (
            await test_session.execute(
                select(Tweets)
                .options(selectinload(Tweets.likes))
                .filter(Tweets.id == tweet_id)
            )
        )
        .unique()
        .scalar_one_or_none()
    )

    assert user not in tweet.likes

    response = await test_client.post(
        f"/tweets/{tweet_id}/likes", headers={"api-key": f"{user.api_key}"}
    )
    await test_session.refresh(tweet)
    assert response.status_code == 201
    assert response.json()["result"]
    assert user in tweet.likes


@pytest.mark.asyncio(scope="session")
async def test_like_tweet_fail(test_client, test_session):
    user = (await test_session.execute(select(Users))).scalars().first()
    tweet_id = user.tweets[0].id

    response = await test_client.post(f"/tweets/{tweet_id}/likes", headers={})
    assert response.status_code == 422
    assert not response.json()["result"]

    response = await test_client.post(
        f"/tweets/{tweet_id}/likes", headers={"api-key": "46"}
    )
    assert response.status_code == 401
    assert not response.json()["result"]

    response = await test_client.post(
        "/tweets/46/likes", headers={"api-key": f"{user.api_key}"}
    )
    assert response.status_code == 404
    assert not response.json()["result"]

    response = await test_client.post(
        f"/tweets/{tweet_id}/likes", headers={"api-key": f"{user.api_key}"}
    )
    assert response.status_code == 405
    assert not response.json()["result"]

    response = await test_client.post(
        "/tweets/not_int/likes", headers={"api-key": f"{user.api_key}"}
    )
    assert response.status_code == 422
    assert not response.json()["result"]


@pytest.mark.asyncio(scope="session")
async def test_unlike_tweet_ok(test_client, test_session):
    user = (await test_session.execute(select(Users))).scalars().first()
    tweet_id = user.tweets[0].id
    tweet = (
        (
            await test_session.execute(
                select(Tweets)
                .options(selectinload(Tweets.likes))
                .filter(Tweets.id == tweet_id)
            )
        )
        .unique()
        .scalar_one_or_none()
    )

    assert user in tweet.likes

    response = await test_client.delete(
        f"/tweets/{tweet_id}/likes", headers={"api-key": f"{user.api_key}"}
    )
    await test_session.refresh(tweet)
    assert response.status_code == 200
    assert response.json()["result"]
    assert user not in tweet.likes


@pytest.mark.asyncio(scope="session")
async def test_unlike_tweet_fail(test_client, test_session):
    user = (await test_session.execute(select(Users))).scalars().first()
    tweet_id = user.tweets[0].id

    response = await test_client.delete(f"/tweets/{tweet_id}/likes", headers={})
    assert response.status_code == 422
    assert not response.json()["result"]

    response = await test_client.delete(
        f"/tweets/{tweet_id}/likes", headers={"api-key": "46"}
    )
    assert response.status_code == 401
    assert not response.json()["result"]

    response = await test_client.delete(
        "/tweets/46/likes", headers={"api-key": f"{user.api_key}"}
    )
    assert response.status_code == 404
    assert not response.json()["result"]

    response = await test_client.delete(
        f"/tweets/{tweet_id}/likes", headers={"api-key": f"{user.api_key}"}
    )
    assert response.status_code == 405
    assert not response.json()["result"]

    response = await test_client.delete(
        "/tweets/not_int/likes", headers={"api-key": f"{user.api_key}"}
    )
    assert response.status_code == 422
    assert not response.json()["result"]


@pytest.mark.asyncio(scope="session")
async def test_all_tweets_ok(test_client, test_session):
    user = (await test_session.execute(select(Users))).scalars().first()
    tweet_id = user.tweets[0].id

    response = await test_client.get("/tweets", headers={"api-key": f"{user.api_key}"})
    assert response.status_code == 200
    assert response.json()["result"]
    assert tweet_id == response.json()["tweets"][0]["id"]
