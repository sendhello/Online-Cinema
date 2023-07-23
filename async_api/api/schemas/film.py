from uuid import UUID

from pydantic import BaseModel


class Film(BaseModel):
    """Модель фильма для вывода в списки."""

    uuid: UUID
    title: str
    imdb_rating: float | None
    new: bool | None


class FullFilm(BaseModel):
    """Модель фильма для страницы фильма"""

    uuid: UUID
    title: str
    imdb_rating: float | None
    description: str | None
    new: bool | None
    genres: str | None
    cast: list[str] = []
