import asyncio

import pytest
from tests.functional.settings import test_settings  # noqa
from tests.functional.testdata.auth import new_user
from tests.functional.utils import generate_tokens

loop = asyncio.get_event_loop()


@pytest.mark.parametrize(
    'user, status_code, result',
    [
        # Ок
        (
            new_user,
            200,
            {
                'first_name': 'Тест',
                'id': '345fa6c5-c138-4f5c-bce5-a35b0f26fced',
                'last_name': 'Тестов',
                'login': 'test',
            },
        ),
    ],
)
@pytest.mark.asyncio
async def test_profile(client, mock_redis, user, status_code, result):
    tokens = await generate_tokens(user)
    access_token = tokens['access_token']
    headers = {"Authorization": f"Bearer {access_token}"}

    response = client.get("api/v1/profile/", headers=headers)
    assert response.status_code == status_code
    data = response.json()
    assert data == result

    redis = await mock_redis()
    await redis.flush()


@pytest.mark.parametrize(
    'user, status_code, result',
    [
        # Ок
        (
            new_user,
            200,
            [
                {'created_at': '2023-04-01T00:00:00', 'user_agent': 'testclient'},
            ],
        ),
    ],
)
@pytest.mark.asyncio
async def test_profile_history(client, mock_redis, user, status_code, result):
    tokens = await generate_tokens(user)
    access_token = tokens['access_token']
    headers = {"Authorization": f"Bearer {access_token}"}

    response = client.get("api/v1/profile/history", headers=headers)
    assert response.status_code == status_code
    data = response.json()
    assert data == result

    redis = await mock_redis()
    await redis.flush()


@pytest.mark.parametrize(
    'user, status_code, result',
    [
        # Ок
        (
            {
                'login': new_user['login'],
                'first_name': new_user['first_name'],
                'last_name': 'Брокенов',
                'current_password': new_user['password'],
            },
            200,
            {
                'id': '345fa6c5-c138-4f5c-bce5-a35b0f26fced',
                'login': 'test',
                'first_name': 'Тест',
                'last_name': 'Брокенов',
            },
        ),
    ],
)
@pytest.mark.asyncio
async def test_profile_update(client, mock_redis, user, status_code, result):
    tokens = await generate_tokens(user)
    access_token = tokens['access_token']
    headers = {"Authorization": f"Bearer {access_token}"}

    response = client.post("api/v1/profile/update", headers=headers, json=user)
    assert response.status_code == status_code
    data = response.json()
    assert data == result

    redis = await mock_redis()
    await redis.flush()


@pytest.mark.parametrize(
    'user, change_password, status_code, result',
    [
        # Ок
        (
            new_user,
            {
                'current_password': new_user['password'],
                'new_password': '123qwe',
            },
            200,
            {
                'id': '345fa6c5-c138-4f5c-bce5-a35b0f26fced',
                'login': 'test',
                'first_name': 'Тест',
                'last_name': 'Тестов',
            },
        ),
    ],
)
@pytest.mark.asyncio
async def test_profile_change_password(
    client, mock_redis, user, change_password, status_code, result
):
    tokens = await generate_tokens(user)
    access_token = tokens['access_token']
    headers = {"Authorization": f"Bearer {access_token}"}

    response = client.post(
        "api/v1/profile/change_password", headers=headers, json=change_password
    )
    assert response.status_code == status_code
    data = response.json()
    assert data == result

    redis = await mock_redis()
    await redis.flush()
