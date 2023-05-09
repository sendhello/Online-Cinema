from enum import Enum


class FilmSort(str, Enum):
    RATING_UP = 'imdb_rating'
    RATING_DOWN = '-imdb_rating'


class GenreSort(str, Enum):
    ID_UP = 'id'
    ID_DOWN = '-id'


class PersonSort(str, Enum):
    ID_UP = 'id'
    ID_DOWN = '-id'


# Время кеширования в Redis
CACHE_TIME = 60 * 5  # 5 минут
