from pydantic import BaseModel
from uuid import UUID


class Genre(BaseModel):
    uuid: UUID
    name: str
