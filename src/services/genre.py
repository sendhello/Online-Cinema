from functools import lru_cache

from redis.asyncio import Redis
from elasticsearch import AsyncElasticsearch, NotFoundError
from fastapi import Depends

from db.elastic import get_elastic
from db.redis import get_redis

from models.film import Genre
from services.base_entity import BaseEntity


class GenreService(BaseEntity):
    name = 'genre'
    index_name = 'genres'

    def __init__(self, redis: Redis, elastic: AsyncElasticsearch,):
        super().__init__(elastic, self.name, self.index_name)
        self.redis = redis

    async def get_genres(self, **kwargs):
        # todo добавить кэширование
        genres = await self.get_items_from_elastic(**kwargs)
        if not genres:
            return []
        return genres

    async def get_genre_by_id(self, genre_id):
        # todo добавить кэширование
        genres = await self._get_genre_from_elastic(genre_id)
        if not genres:
            return []
        return genres

    async def _get_genre_from_elastic(self, genre_id: str) -> Genre | None:
        try:
            doc = await self.elastic.get(index=self.index_name, id=genre_id)
        except NotFoundError:
            return

        genre = doc['_source'].get('genre')
        if genre and isinstance(genre, str):
            doc['_source'][self.name] = [{'id': item, self.title_field_name: item} for item in genre.split(' ')]
        return Genre(**doc['_source'])


@lru_cache()
def get_genre_service(
        redis: Redis = Depends(get_redis),
        elastic: AsyncElasticsearch = Depends(get_elastic),
) -> GenreService:
    return GenreService(redis, elastic)
