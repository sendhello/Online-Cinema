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
            201,
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
async def test_create_user(client, mock_redis, user, status_code, result):
    response = client.post('api/v1/auth/signup', json=user)
    assert response.status_code == status_code
    data = response.json()
    assert data == result

    redis = await mock_redis()
    await redis.flush()


@pytest.mark.parametrize(
    'login_data, status_code, result_keys',
    [
        # Ок
        (
            {'login': new_user['login'], 'password': new_user['password']},
            200,
            ['access_token', 'refresh_token'],
        ),
    ],
)
@pytest.mark.asyncio
async def test_login(client, mock_redis, login_data, status_code, result_keys):
    response = client.post("api/v1/auth/login", json=login_data)
    assert response.status_code == status_code
    data = response.json()
    assert list(data.keys()) == result_keys

    redis = await mock_redis()
    await redis.flush()


@pytest.mark.parametrize(
    'user, status_code, result_keys',
    [
        # Ок
        (new_user, 200, ['access_token', 'refresh_token']),
    ],
)
@pytest.mark.asyncio
async def test_refresh(client, mock_redis, user, status_code, result_keys):
    tokens = await generate_tokens(user)
    refresh_token = tokens['refresh_token']
    headers = {"Authorization": f"Bearer {refresh_token}"}
    response = client.post("api/v1/auth/refresh", headers=headers)
    assert response.status_code == status_code
    data = response.json()
    assert list(data.keys()) == result_keys

    redis = await mock_redis()
    await redis.flush()


@pytest.mark.parametrize(
    'user, status_code, result',
    [
        # Ок
        (new_user, 200, {}),
    ],
)
@pytest.mark.asyncio
async def test_logout(client, mock_redis, user, status_code, result):
    tokens = await generate_tokens(user)
    access_token = tokens['access_token']
    headers = {"Authorization": f"Bearer {access_token}"}
    response = client.post("api/v1/auth/logout", headers=headers)
    assert response.status_code == status_code
    data = response.json()
    assert data == result

    redis = await mock_redis()
    await redis.flush()
