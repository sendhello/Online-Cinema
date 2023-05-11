from functools import lru_cache

import orjson
from elasticsearch import AsyncElasticsearch, NotFoundError
from fastapi import Depends
from redis.asyncio import Redis

from db.elastic import get_elastic
from db.redis import get_redis

from models.genre import Genre
from services.base_entity import BaseEntity


class GenreService(BaseEntity):
    name = 'genre'
    index_name = 'genres'

    def __init__(self, redis: Redis, elastic: AsyncElasticsearch):
        super().__init__(
            redis=redis,
            elastic=elastic,
            entity_name=self.name,
            index_name=self.index_name
        )

    async def get_genres(self, **kwargs):
        key = f"genres:{'-'.join(str(val) for val in kwargs.values())}"
        genres = await self._get_genres_from_cache(key)

        if not genres:
            genres = await self.get_items_from_elastic(**kwargs)

            await self._put_genres_to_cache(key, genres)

        return genres

    async def get_genre_by_id(self, genre_id):
        genre = await self._get_genre_from_cache(genre_id)

        if not genre:
            genre = await self._get_genre_from_elastic(genre_id)
            if not genre:
                return None

            await self._put_genre_to_cache(genre)

        return genre

    async def _get_genre_from_elastic(self, genre_id: str) -> Genre | None:
        try:
            doc = await self.elastic.get(index=self.index_name, id=genre_id)
        except NotFoundError:
            return

        genre = doc['_source'].get('genre')
        if genre and isinstance(genre, str):
            doc['_source'][self.name] = [{'id': item, self.title_field_name: item} for item in genre.split(' ')]
        return Genre(**doc['_source'])

    async def _put_genre_to_cache(self, genre: Genre):
        key = f'genre:{genre.uuid}'
        await self._put_to_cache(key, genre.json(by_alias=True))

    async def _put_genres_to_cache(self, key, genres: list[Genre]):
        data = [genre.dict(by_alias=True) for genre in genres]
        await self._put_to_cache(key, orjson.dumps(data))

    async def _get_genre_from_cache(self, genre_id: str) -> Genre | None:
        key = f'genre:{genre_id}'
        data = await self._get_from_cache(key)
        if data is None:
            return None

        genre = Genre.parse_raw(data)
        return genre

    async def _get_genres_from_cache(self, key) -> list[Genre] | None:
        data = await self._get_from_cache(key)
        if data is None:
            return None

        genres = [Genre.parse_obj(genre_raw) for genre_raw in orjson.loads(data)]
        return genres


@lru_cache()
def get_genre_service(
        redis: Redis = Depends(get_redis),
        elastic: AsyncElasticsearch = Depends(get_elastic),
) -> GenreService:
    return GenreService(redis, elastic)
