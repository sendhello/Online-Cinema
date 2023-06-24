import logging
from functools import lru_cache

import orjson
from elasticsearch import AsyncElasticsearch
from fastapi import Depends
from redis.asyncio import Redis

from constants import Index
from db.elastic import get_elastic
from db.redis import get_redis
from models.person import Person

from .base import BaseService
from .elastic_db import ElasticRequest, QueryFilter, QueryType
from .redis_cache import RedisCache

logger = logging.getLogger(__name__)


class PersonService(BaseService):
    async def filter(
            self,
            page_size: int,
            page_number: int,
            query: str | None = None,
    ) -> list[Person]:
        model_name = self.request.model.__name__.lower()
        key = f'filter:{model_name}-{page_size}-{page_number}-{query}'

        data = await self.cache.get_from_cache(key)
        if data is not None:
            return [self.request.model.parse_obj(raw_entity) for raw_entity in orjson.loads(data)]

        filters = []

        if query is not None:
            filters.append(
                QueryFilter(
                    type=QueryType.MULTI_MATCH,
                    query=query,
                    fields=['full_name'],
                )
            )

        entities = await self.request.filter(
            filters=filters,
            size=page_size,
            page_number=page_number,
        )

        data = [entity.dict(by_alias=True) for entity in entities]
        await self.cache.put_to_cache(key, orjson.dumps(data))

        return entities


@lru_cache()
def get_person_service(
        redis: Redis = Depends(get_redis),
        elastic: AsyncElasticsearch = Depends(get_elastic),
) -> PersonService:
    return PersonService(
        cache=RedisCache(redis),
        request=ElasticRequest(elastic, index=Index.PERSONS),
    )
