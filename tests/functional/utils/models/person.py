from pydantic import BaseModel
from functional.utils.models.base_models import UUIDMixin, IDMixin
from functional.utils.models.film import EsFilm


class PersonUUID(UUIDMixin):
    full_name: str


class PersonID(IDMixin):
    full_name: str


class PersonFilm(UUIDMixin):
    roles: list[str]


class FilmShort(BaseModel):
    uuid: str
    title: str
    imdb_rating: float


class PersonDescription(UUIDMixin):
    full_name: str
    films: list[PersonFilm]


class PersonsData(BaseModel):
    es_data: list[PersonID]
    expected_data: list[PersonUUID]


class PersonData(BaseModel):
    person_uuid: str
    es_data: list[PersonID]
    expected_data: PersonDescription


class PersonFilmsData(BaseModel):
    person_uuid: str
    es_data: dict[str, list[PersonID | EsFilm]]
    expected_data: list[FilmShort]


class PersonSearchData(BaseModel):
    params: str
    es_data: dict[str, list[PersonID | EsFilm]]
    expected_data: list[PersonDescription]
