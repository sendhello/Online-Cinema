from uuid import UUID

from .base_model import Model


class BaseUser(Model):
    first_name: str
    last_name: str


class UserLogin(Model):
    login: str
    password: str


class UserCreate(UserLogin, BaseUser):
    pass


class UserInDB(BaseUser):
    id: UUID
