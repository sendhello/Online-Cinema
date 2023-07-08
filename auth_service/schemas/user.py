from pydantic import EmailStr

from .base import Model
from .mixins import IdMixin
from .roles import RoleInDB


class BaseUser(Model):
    email: EmailStr


class PersonalUser(Model):
    first_name: str
    last_name: str


class UserLogin(BaseUser):
    password: str


class UserCreate(UserLogin, PersonalUser):
    pass


class UserCreated(BaseUser, PersonalUser, IdMixin):
    """Модель пользователя при выводе после регистрации."""

    pass


class UserInDB(UserCreated):
    """Модель пользователя в БД."""

    login: str | None
    role: RoleInDB | None


class UserUpdate(BaseUser, PersonalUser):
    """Модель пользователя для обновления данных."""

    current_password: str


class UserChangePassword(Model):
    """Модель пользователя для смены пароля."""

    current_password: str
    new_password: str
