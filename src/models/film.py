from pydantic import BaseModel, Field

from . import Model


class UUIDMixin(BaseModel):
    uuid: str = Field(alias='id')


class Genre(Model, UUIDMixin):
    name: str


class Person(Model, UUIDMixin):
    full_name: str = Field(alias='name')


class Film(Model, UUIDMixin):
    """Модель фильма из БД.
    """
    title: str
    imdb_rating: float
    description: str | None
    genre: list[str] = []
    actors: list[Person] = []
    writers: list[Person] = []
    directors: list[Person] = []
    actors_names: list[str] = []
    writers_names: list[str] = []
