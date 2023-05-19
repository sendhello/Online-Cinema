from pydantic import BaseModel
from functional.utils.models.base_models import UUIDMixin
from functional.utils.models.film import Film


class Person(UUIDMixin):
    full_name: str


class PersonFilm(BaseModel):
    id: str
    roles: list[str]


class FilmShort(BaseModel):
    uuid: str
    title: str
    imdb_rating: float


class PersonDescription(UUIDMixin):
    full_name: str
    films: list[PersonFilm]


class PersonsData(BaseModel):
    es_data: list[Person]
    expected_data: list[Person]


class PersonData(BaseModel):
    person_uuid: str
    es_data: list[Person]
    expected_data: PersonDescription


class PersonFilmsData(BaseModel):
    person_uuid: str
    es_data: dict[str, list[Person | Film]]
    expected_data: list[FilmShort]


class PersonSearchData(BaseModel):
    params: str
    es_data: dict[str, list[Person | Film]]
    expected_data: list[Person]