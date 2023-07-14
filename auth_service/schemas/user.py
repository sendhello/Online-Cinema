from models import Rules
from pydantic import EmailStr, Field, validator

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


class UserResponse(UserCreated):
    """Модель пользователя при авторизации."""

    login: str | None
    role: str | None
    rules: list[str] = Field(default_factory=list)

    @validator('role', pre=True)
    def convert_role(cls, v: RoleInDB | str | None):
        if v is None:
            return None

        if isinstance(v, RoleInDB):
            return v.title

        return v

    @validator('rules', pre=True)
    def convert_rules(cls, v: list[Rules]):
        if v is None:
            return None

        if isinstance(v, list):
            new_v = []
            for el in v:
                if isinstance(el, Rules):
                    new_v.append(el.value)
                else:
                    new_v.append(el)

            return new_v

        return v


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
