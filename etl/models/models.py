import orjson
from pydantic import BaseModel, Field


def orjson_dumps(v, *, default):
    return orjson.dumps(v, default=default).decode()


class UUIDMixin(BaseModel):
    uuid: str = Field(alias='id')


class OrjsonMixin(BaseModel):
    class Config:
        json_loads = orjson.loads
        json_dumps = orjson_dumps


class Genre(UUIDMixin, OrjsonMixin):
    name: str


class Person(UUIDMixin, OrjsonMixin):
    full_name: str = Field(alias='name')


class Film(UUIDMixin, OrjsonMixin):
    title: str
    imdb_rating: float
    description: str = ''
    genre: list[Genre] = []
    actors: list[Person] = []
    writers: list[Person] = []
    directors: list[Person] = []
