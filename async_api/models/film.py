from .base import Model, UUIDMixin


class Person(Model, UUIDMixin):
    name: str


class Film(Model, UUIDMixin):
    """Модель фильма из БД."""

    title: str
    imdb_rating: float | None
    description: str | None
    genre: str | None
    new: bool | None
    actors: list[Person] = []
    writers: list[Person] = []
    directors: list[Person] = []
    actors_names: list[str] = []
    writers_names: list[str] = []


class FilmShort(Model):
    id: str
    title: str
    imdb_rating: float
    new: bool | None
