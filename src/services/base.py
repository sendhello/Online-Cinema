from abc import ABC, abstractmethod

from . import AbstractService
from .elastic_db import ElasticRequest
from .redis_cache import RedisCache


class BaseService(AbstractService, ABC):
    def __init__(self, cache: RedisCache, request: ElasticRequest):
        self.cache = cache
        self.request = request

    async def get_by_id(self, id_: str):
        """Метод получения объекта по id.
        """
        key = f'id:{id_}'
        data = await self.cache.get_from_cache(key)

        if data is not None:
            return self.request.model.parse_raw(data)

        entity = await self.request.get_by_id(id_)
        if not entity:
            return None

        data = entity.json(by_alias=True)
        await self.cache.put_to_cache(key, data)

        return entity

    @abstractmethod
    async def filter(self, **kwargs):
        """Метод получения списка объектов по параметрам.
        """
        pass
