from enum import Enum
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field


class Rules(str, Enum):
    """Права пользователя."""

    anonymous_rules = 'anonymous_rules'
    user_rules = 'user_rules'
    subscription_rules = 'subscription_rules'
    admin_rules = 'admin_rules'


class User(BaseModel):
    """Модель пользователя."""

    id: UUID = Field(title='ID пользователя')
    email: EmailStr = Field(title='Email пользователя')
    first_name: str = Field(title='Имя')
    last_name: str = Field(title='Фамилия')
    login: str | None = Field(title='Логин')
    role: str | None = Field(title='Роль')
    rules: list[str] = Field(title='Список прав')

    @property
    def is_subscriber(self):
        """Является ли пользователь подписчиком сервиса."""
        allowed_rules = {Rules.subscription_rules, Rules.admin_rules}
        if allowed_rules & set(self.rules):
            return True

        return False
