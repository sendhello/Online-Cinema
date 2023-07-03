import os
import sys
from datetime import datetime
from uuid import UUID

sys.path.insert(0, f"{os.getcwd()}/auth_service")

import pytest
from fastapi.testclient import TestClient
from models import History, User
from models.mixins import CRUDMixin
from tests.functional.redis import redis

from auth_service.main import app

db = [
    {
        'login': 'test',
        'password': 'password',
        'first_name': 'Тест',
        'last_name': 'Тестов',
    }
]


@pytest.fixture
def mock_redis():
    async def inner():
        return redis

    return inner


@pytest.fixture
def mock_save():
    async def inner(self: CRUDMixin, commit: bool = True):
        if getattr(self, 'id', '') is None:
            self.id = UUID('345fa6c5-c138-4f5c-bce5-a35b0f26fced')
        if getattr(self, 'created_at', '') is None:
            self.created_at = datetime(2023, 4, 1)
        if getattr(self, 'updated_at', '') is None:
            self.updated_at = datetime(2023, 4, 1)

        return self

    return inner


@pytest.fixture
def mock_get_by_login():
    async def inner(username: str):
        user = User(**db[0])
        user.id = UUID('345fa6c5-c138-4f5c-bce5-a35b0f26fced')
        return user

    return inner


@pytest.fixture
def mock_check_password():
    def inner(self, password: str) -> bool:
        return password == 'password'

    return inner


@pytest.fixture
def mock_change_password():
    async def inner(self, new_password: str) -> bool:
        user = User(**db[0])
        user.id = UUID('345fa6c5-c138-4f5c-bce5-a35b0f26fced')
        return user

    return inner


@pytest.fixture
def mock_get_by_user_id():
    async def inner(user_id: UUID):
        history = History(
            user_id=UUID('345fa6c5-c138-4f5c-bce5-a35b0f26fced'),
            user_agent='testclient',
        )
        history.created_at = datetime(2023, 4, 1)
        return [history]

    return inner


@pytest.fixture
def client(
    monkeypatch,
    mock_redis,
    mock_save,
    mock_get_by_login,
    mock_check_password,
    mock_change_password,
    mock_get_by_user_id,
):
    # monkeypatch.setattr('schemas.token.get_redis', mock_redis)
    monkeypatch.setattr('db.redis_db.redis', redis)
    monkeypatch.setattr(CRUDMixin, 'save', mock_save)
    monkeypatch.setattr(User, 'get_by_login', mock_get_by_login)
    monkeypatch.setattr(User, 'check_password', mock_check_password)
    monkeypatch.setattr(User, 'change_password', mock_change_password)
    monkeypatch.setattr(History, 'get_by_user_id', mock_get_by_user_id)

    return TestClient(app)
