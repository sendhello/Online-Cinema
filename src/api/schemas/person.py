from pydantic import BaseModel, Field


class UUIDMixin(BaseModel):
    uuid: str = Field(alias='id')


class Person(UUIDMixin):
    full_name: str


class PersonFilm(BaseModel):
    uuid: str
    roles: list[str]


class PersonDescription(UUIDMixin):
    """
    /api/v1/persons/<uuid:UUID>/
    """
    full_name: str
    films: list[PersonFilm]
