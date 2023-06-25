from .base_models import IDMixin, UUIDMixin
from pydantic import BaseModel


class GenreUUID(UUIDMixin):
    name: str


class GenreID(IDMixin):
    name: str


class GenreData(BaseModel):
    genre_id: str
    es_data: list[GenreID]
    expected_data: GenreUUID


class GenresListData(BaseModel):
    es_data: list[GenreID]
    expected_data: list[GenreUUID]
