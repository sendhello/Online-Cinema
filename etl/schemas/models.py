from pydantic import BaseModel, Field


class MoviePerson(BaseModel):
    """Модель персоны для индекса."""

    id: str
    name: str


class Genre(BaseModel):
    """Модель жанра для индекса."""

    id: str
    name: str


class Movie(BaseModel):
    """Модель индекса."""

    id: str
    imdb_rating: float | None
    genre: str | None
    title: str
    description: str | None
    new: bool = Field(default_factory=bool)
    director: str = Field(default_factory=str)
    actors_names: list[str] = Field(default_factory=list)
    writers_names: list[str] = Field(default_factory=list)
    actors: list[MoviePerson] = Field(default_factory=list)
    writers: list[MoviePerson] = Field(default_factory=list)


class Person(BaseModel):
    """Модель персоны для индекса."""

    id: str
    full_name: str
