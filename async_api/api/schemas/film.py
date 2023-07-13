from uuid import UUID

from pydantic import BaseModel


class Film(BaseModel):
    """Модель фильма для вывода в списки.
    """
    uuid: UUID
    title: str
    imdb_rating: float


class FullFilm(BaseModel):
    """Модель фильма для страницы фильма"""
    uuid: UUID
    title: str
    imdb_rating: float
    description: str | None
    genres: str | None
    cast: list[str] = []
