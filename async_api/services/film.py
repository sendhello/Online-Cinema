import logging
from functools import lru_cache
from uuid import UUID

import orjson
from elasticsearch import AsyncElasticsearch
from fastapi import Depends
from redis.asyncio import Redis

from constants import FilmSort, Index, LogicType
from db.elastic import get_elastic
from db.redis_db import get_redis
from models.film import Film

from .base import BaseService
from .elastic_db import ElasticRequest, QueryFilter, QueryType
from .redis_cache import RedisCache

logger = logging.getLogger(__name__)


class FilmService(BaseService):
    async def filter(
            self,
            page_size: int,
            page_number: int,
            sort: FilmSort | None = None,
            genre: str | None = None,
            person_id: UUID | None = None,
            query: str | None = None,
    ) -> list[Film]:
        model_name = self.request.model.__name__.lower()
        key = f'filter:{model_name}-{page_size}-{page_number}-{sort}-{genre}-{person_id}-{query}'

        data = await self.cache.get_from_cache(key)
        if data is not None:
            return [self.request.model.parse_obj(raw_entity) for raw_entity in orjson.loads(data)]

        filters = []

        if genre is not None:
            filters.append(
                QueryFilter(
                    type=QueryType.MATCH,
                    query=genre,
                    fields=['genre'],
                )
            )

        if person_id is not None:
            filters.append(
                QueryFilter(
                    type=QueryType.NESTED,
                    query=str(person_id),
                    fields=['actors.id', 'writers.id'],
                    fields_type=LogicType.SHOULD,
                )
            )

        if query is not None:
            filters.append(
                QueryFilter(
                    type=QueryType.MULTI_MATCH,
                    query=query,
                    fields=['title', 'description', 'actors_names', 'writers_names', 'director'],
                )
            )

        entities = await self.request.filter(
            sort_texts=[sort] if sort is not None else None,
            filters=filters,
            size=page_size,
            page_number=page_number,
        )

        data = [entity.dict(by_alias=True) for entity in entities]
        await self.cache.put_to_cache(key, orjson.dumps(data))

        return entities


@lru_cache()
def get_film_service(
        redis: Redis = Depends(get_redis),
        elastic: AsyncElasticsearch = Depends(get_elastic),
) -> FilmService:
    return FilmService(
        cache=RedisCache(redis),
        request=ElasticRequest(elastic, index=Index.MOVIES),
    )
