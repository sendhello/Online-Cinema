from uuid import UUID

from pydantic import EmailStr

from .base import Model
from enum import Enum


class Rules(str, Enum):
    anonymous_rules = "anonymous_rules"
    user_rules = "user_rules"
    subscription_rules = "subscription_rules"
    admin_rules = "admin_rules"


class User(Model):
    id: UUID
    login: str | None
    email: EmailStr
    first_name: str | None
    last_name: str | None
    role: str | None
    rules: list[Rules]
