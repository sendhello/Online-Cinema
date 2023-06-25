import logging
from functools import lru_cache

import orjson
from elasticsearch import AsyncElasticsearch
from fastapi import Depends
from redis.asyncio import Redis

from constants import Index
from db.elastic import get_elastic
from db.redis_db import get_redis
from models.genre import Genre

from .base import BaseService
from .elastic_db import ElasticRequest
from .redis_cache import RedisCache

logger = logging.getLogger(__name__)


class GenreService(BaseService):
    async def filter(
            self,
            page_size: int,
            page_number: int,
    ) -> list[Genre]:
        model_name = self.request.model.__name__.lower()
        key = f'filter:{model_name}-{page_size}-{page_number}'
        data = await self.cache.get_from_cache(key)
        if data is not None:
            return [self.request.model.parse_obj(raw_entity) for raw_entity in orjson.loads(data)]

        entities = await self.request.filter(
            size=page_size,
            page_number=page_number,
        )

        data = [entity.dict(by_alias=True) for entity in entities]
        await self.cache.put_to_cache(key, orjson.dumps(data))

        return entities


@lru_cache()
def get_genre_service(
        redis: Redis = Depends(get_redis),
        elastic: AsyncElasticsearch = Depends(get_elastic),
) -> GenreService:
    return GenreService(
        cache=RedisCache(redis),
        request=ElasticRequest(elastic, index=Index.GENRES),
    )
