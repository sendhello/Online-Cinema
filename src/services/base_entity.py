import logging

from elasticsearch import AsyncElasticsearch, NotFoundError
from pydantic import BaseModel
from redis.asyncio import Redis

from models.genre import Genre
from models.person import Person

ENTITIES_SETTINGS = {
    'genre': {
        'title_field_name': 'name',
        'model_class': Genre,
    },
    'person': {
        'title_field_name': 'full_name',
        'model_class': Person,
    },
}


class BaseEntity(BaseModel):
    movies_index_name = 'movies'

    def __init__(
            self,
            redis: Redis,
            elastic: AsyncElasticsearch,
            entity_name: str,
            index_name: str,
    ):
        super().__init__(redis, elastic)
        self.name = entity_name
        self.index_name = index_name

        entity_settings = ENTITIES_SETTINGS[entity_name]
        self.title_field_name = entity_settings.get('title_field_name')
        self.model_class = entity_settings.get('model_class')
        self.model_class_sort = entity_settings.get('model_class_sort')

    def _get_body(
            self,
            query: str | None = None,
            item_id: str | None = None,
    ) -> dict | None:
        if item_id:
            return {
                'query': {
                    'query_string': {
                        'default_field': self.name,
                        'query': item_id
                    }
                }
            }

        if query:
            return {
                'query': {
                    'match': {
                        self.title_field_name: {
                            'query': query,
                            'fuzziness': 1,
                            'operator': 'and',
                            'analyzer': 'ru_en'
                        }
                    }
                }
            }

    def _get_sort_by_id(self, sort: str) -> list:
        match sort:
            case self.model_class_sort.ID_UP:
                sort = [{"id": "asc"}]
            case self.model_class_sort.ID_DOWN:
                sort = [{"id": "desc"}]
            case _:
                sort = []
        sort.append({"_score": "desc"})
        return sort

    def _get_transformed_doc(self, doc: dict):
        item = doc['_source'].get(self.name)
        if item:
            doc['_source']['person'] = [{'id': item, self.title_field_name: item_} for item_ in item.split(' ')]
        logging.info(doc['_source'])
        result = self.model_class(**doc['_source'])
        return result

    async def get_entity_from_elastic(self, entity_id: str) -> Person | Genre | None:
        try:
            doc = await self.elastic.get(index=self.index_name, id=entity_id)
        except NotFoundError:
            return

        entity = doc['_source'].get(self.name)
        if isinstance(entity, str):
            doc['_source'][self.name] = [{'id': item, self.title_field_name: item} for item in entity.split(' ')]
        return self.model_class(**doc['_source'])

    async def get_items_from_elastic(
            self,
            page_size: int,
            page_number: int,
            item_id: str = None,
            query: str = None,
            sort: str = None,
    ):
        body = self._get_body(query, item_id)
        sort = self._get_sort_by_id(sort)

        try:
            docs = await self.elastic.search(
                index=self.index_name,
                body=body,
                params={
                    'size': page_size,
                    'from': page_number - 1,
                    'sort': sort,
                })
        except NotFoundError:
            return []

        return [self._get_transformed_doc(doc) for doc in docs['hits']['hits']]
