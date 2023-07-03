from .base import Model
from .mixins import IdMixin
from .roles import RoleInDB


class BaseUser(Model):
    first_name: str
    last_name: str


class UserLogin(Model):
    login: str
    password: str


class UserCreate(BaseUser, UserLogin):
    pass


class UserInDB(BaseUser, IdMixin):
    """Модель пользователя в БД."""

    login: str


class UserWithRole(UserInDB):
    """Модель пользователя с ролью."""

    role: RoleInDB | None


class UserUpdate(BaseUser):
    """Модель пользователя для обновления данных."""

    login: str
    current_password: str


class UserChangePassword(Model):
    """Модель пользователя для смены пароля."""

    current_password: str
    new_password: str
