import logging

from constants import CACHE_TIME
from redis.asyncio import Redis

from . import AbstractCache


logger = logging.getLogger(__name__)


class RedisCache(AbstractCache):
    def __init__(self, redis: Redis):
        self.redis = redis

    async def put_to_cache(self, key: str, data: bytes):
        """Метод записи в кеш."""
        logger.info(f'Запись результатов запроса в кеш: key = {key}')
        await self.redis.set(key, data, CACHE_TIME)

    async def get_from_cache(self, key: str) -> bytes | None:
        """Метод получения данных из кеша."""
        data = await self.redis.get(key)
        if not data:
            return None

        logger.info(f'Получение данных из кеша: key = {key}')
        return data
