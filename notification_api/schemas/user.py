from typing import Any
from uuid import UUID

from pydantic import BaseModel, EmailStr


class User(BaseModel):
    id: UUID
    email: EmailStr
    first_name: str
    last_name: str
    login: str | None
    role: Any | None
