from pydantic import Field, BaseModel

from models.film import UUIDMixin
from api.schemas.film import Film
from typing import Dict
from pydantic import Field


class Person(UUIDMixin):
    full_name: str


class PersonDescription(BaseModel):
    """
    /api/v1/persons/<uuid:UUID>/
    """
    uuid: str = Field(alias='id')
    full_name: str
    films: list[Dict[str, list | str]]


class FilmPerson(UUIDMixin, Film):
    pass
