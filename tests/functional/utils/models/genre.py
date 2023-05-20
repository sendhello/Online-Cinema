from pydantic import BaseModel
from functional.utils.models.base_models import UUIDMixin, IDMixin


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
