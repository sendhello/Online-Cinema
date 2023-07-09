import logging
from abc import ABC, abstractmethod


logger = logging.getLogger(__name__)


class AbstractCache(ABC):
    @abstractmethod
    async def put_to_cache(self, key, data):
        """Метод записи в кеш."""
        pass

    @abstractmethod
    async def get_from_cache(self, key):
        """Метод получения данных из кеша."""
        pass


class AbstractDBRequest(ABC):
    @abstractmethod
    async def get_by_id(self, id_: str):
        """Метод получения объекта по id."""
        pass

    @abstractmethod
    async def filter(self, **kwargs):
        """Метод получения списка объектов по параметрам."""
        pass


class AbstractService(ABC):
    @abstractmethod
    def __init__(self, cache: AbstractCache, request: AbstractDBRequest):
        self.cache = cache
        self.request = request

    @abstractmethod
    async def get_by_id(self, id_: str):
        """Метод получения объекта по id."""
        pass

    @abstractmethod
    async def filter(self, **kwargs):
        """Метод получения списка объектов по параметрам."""
        pass
