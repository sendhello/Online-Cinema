from typing import Any

from pydantic import BaseModel


class HTTPResponse(BaseModel):
    body: Any
    status: int


class UUIDMixin(BaseModel):
    uuid: str


class IDMixin(BaseModel):
    id: str
