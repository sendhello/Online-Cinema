from uuid import UUID

from pydantic import BaseModel


class UUIDMixin(BaseModel):
    uuid: UUID


class Person(UUIDMixin):
    full_name: str


class PersonFilm(UUIDMixin):
    roles: list[str]


class PersonDescription(UUIDMixin):
    """
    /api/v1/persons/<uuid:UUID>/
    """

    full_name: str
    films: list[PersonFilm]
