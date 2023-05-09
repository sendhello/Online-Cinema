import logging
from typing import Optional

from elasticsearch import AsyncElasticsearch
from redis.asyncio import Redis

from constants import CACHE_TIME

logger = logging.getLogger(__name__)


class BaseService:
    def __init__(self, redis: Redis, elastic: AsyncElasticsearch):
        self.redis = redis
        self.elastic = elastic

    async def _put_to_cache(self, key, json_data: bytes):
        logger.info(f'Запись результатов запроса в кеш: key = {key}')
        await self.redis.set(key, json_data, CACHE_TIME)

    async def _get_from_cache(self, key) -> Optional[bytes]:
        json_data = await self.redis.get(key)
        if not json_data:
            return None

        logger.info(f'Получение данных из кеша: key = {key}')
        return json_data
