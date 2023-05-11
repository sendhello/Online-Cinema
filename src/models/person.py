from pydantic import BaseModel
from . import Model, UUIDMixin


class Person(Model, UUIDMixin):
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
