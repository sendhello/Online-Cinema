import logging
from functools import lru_cache

import orjson
from elasticsearch import AsyncElasticsearch
from fastapi import Depends
from redis.asyncio import Redis

from constants import FilmSort, Index
from db.elastic import get_elastic
from db.redis import get_redis
from models.genre import Genre

from .base import BaseService
from .elastic_db import ElasticRequest, Query, QueryType
from .redis_cache import RedisCache

logger = logging.getLogger(__name__)


class GenreService(BaseService):
    async def filter(
            self,
            page_size: int,
            page_number: int,
            sort: FilmSort | None = None,
            genre: str | None = None,
            query: str | None = None,
    ) -> list[Genre]:
        key = f'filter:{page_size}-{page_number}-{sort}-{genre}-{query}'
        data = await self.cache.get_from_cache(key)
        if data is not None:
            entities = [self.request.model.parse_obj(raw_entity) for raw_entity in orjson.loads(data)]

        else:
            queries = []

            if genre is not None:
                queries.append(
                    Query(
                        type=QueryType.MATCH,
                        query=genre,
                        fields=['genre'],
                    )
                )

            if query is not None:
                queries.append(
                    Query(
                        type=QueryType.MULTI_MATCH,
                        query=query,
                        fields=['title', 'description', 'actors_names', 'director', 'writers_names', 'genre'],
                    )
                )

            entities = await self.request.filter(
                sort_texts=[sort] if sort is not None else None,
                queries=queries,
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
