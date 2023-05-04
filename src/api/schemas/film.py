from pydantic import BaseModel


class Film(BaseModel):
    """Модель фильма для вывода в списки.
    """
    uuid: str
    title: str
    imdb_rating: float


class FullFilm(BaseModel):
    """Модель фильма для страницы фильма"""
    uuid: str
    title: str
    imdb_rating: float
    description: str | None
    genres: list[str] = []
    cast: list[str] = []
