from enum import Enum


class FilmSort(str, Enum):
    RATING_UP = 'imdb_rating'
    RATING_DOWN = '-imdb_rating'


# Время кеширования в Redis
FILM_CACHE_EXPIRE_IN_SECONDS = 60 * 5  # 5 минут
