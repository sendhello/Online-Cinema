from enum import Enum


class FilmSort(str, Enum):
    RATING_UP = 'imdb_rating'
    RATING_DOWN = '-imdb_rating'


class Index(str, Enum):
    """Индексы в Elastic DB."""

    MOVIES = 'movies'
    GENRES = 'genres'
    PERSONS = 'persons'


class QueryType(str, Enum):
    MATCH = 'match'
    MULTI_MATCH = 'multi_match'
    NESTED = 'nested'
    TERMS = 'terms'


class LogicType(str, Enum):
    MUST = 'must'
    SHOULD = 'should'


# Время кеширования в Redis
CACHE_TIME = 60 * 5  # 5 минут
