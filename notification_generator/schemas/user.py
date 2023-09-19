from uuid import UUID

from pydantic import EmailStr

from .base import Model


class User(Model):
    id: UUID
    login: str | None
    email: EmailStr
    first_name: str | None
    last_name: str | None
