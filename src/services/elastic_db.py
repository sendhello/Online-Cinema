import logging
from enum import Enum
from http import HTTPStatus

import jmespath
from elasticsearch import AsyncElasticsearch, BadRequestError, ConnectionError, NotFoundError
from fastapi import HTTPException
from pydantic import BaseModel, Field, validator

from constants import Index, QueryType
from models.film import Film
from models.genre import Genre
from models.person import Person

from . import AbstractDBRequest

logger = logging.getLogger(__name__)


ModelType = Film | Person | Genre
ModelMap = {
    Index.MOVIES: Film,
    Index.PERSONS: Person,
    Index.GENRES: Genre,
}


class Query(BaseModel):
    """Модель запроса для поиска.
    """
    type: QueryType = Field(title='Тип поиска')
    query: str = Field(title='Текст запроса')
    fields: list[str] = Field(title='Список полей для поиска')

    @validator('fields')
    def validate_fields(cls, val: list[str]) -> list[str]:
        """Валидация наличия полей в поле fields, список не должен быть пустым
        """
        if not val:
            raise ValueError('Поле fields не может быть пустым списком')

        return val


class ElasticRequest(AbstractDBRequest):
    def __init__(self, elastic: AsyncElasticsearch, index: Index):
        self.elastic = elastic
        self.index = index

        model = ModelMap.get(self.index)
        if model is None:
            raise ValueError(f'Не найдена модель индекса {self.index}')

        self.model = model

    async def get_by_id(self, id_: str) -> ModelType | None:
        """Метод получения объекта по id.
        """
        try:
            doc = await self.elastic.get(index=self.index, id=id_)

        except NotFoundError:
            return None

        except ConnectionError as e:
            raise HTTPException(status_code=HTTPStatus.INTERNAL_SERVER_ERROR, detail=e.message)

        return self.model(**doc['_source'])

    async def filter(self, **kwargs):
        """Метод получения списка объектов по параметрам.

        :arg sort_texts - список сортировок, формата 'field' или '-field'
        :arg queries - список поисковых запросов типа Query
        :arg size - пагинация: количество элементов на странице
        :arg page_number - пагинация: номер страницы
        """
        sort_texts: list[str] | None = kwargs.get('sort_texts')
        queries: list[Query] | None = kwargs.get('queries')
        size: int = kwargs.get('size')
        page_number: int = kwargs.get('page_number')

        if queries:
            must = []
            for query in queries:
                if query.type == QueryType.MULTI_MATCH:
                    must.append({
                        'multi_match': {
                            "query": query.query,
                            "fields": query.fields,
                            "fuzziness": "auto"
                        }
                    })

                if query.type == QueryType.MATCH:
                    must.extend(
                        {
                            'match': {
                                field: query.query
                            }
                        } for field in query.fields
                    )

            query = {
                "bool": {
                    "must": must
                }
            }

        else:
            query = {'match_all': {}}

        sort = []
        for sort_text in sort_texts or []:
            sort_type = 'desc' if sort_text.startswith('-') else 'asc'
            sort_field = sort_text.strip('-')
            sort.append({sort_field: sort_type})

        sort.append({"_score": "desc"})

        try:
            logger.debug(f"{sort=}")
            logger.debug(f"{query=}")
            response = await self.elastic.search(
                index=self.index,
                query=query,
                sort=sort,
                size=size,
                from_=(page_number - 1) * size
            )
        except BadRequestError as e:
            error_message = jmespath.search('error.root_cause[0].reason', e.body)
            raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail=error_message)

        except ConnectionError as e:
            raise HTTPException(status_code=HTTPStatus.INTERNAL_SERVER_ERROR, detail=e.message)

        hits = response.get('hits', {}).get('hits', [])
        logging.debug(f"response[0]: {hits[0]['_source']}" if hits else '{}')
        entities = [self.model(**hit['_source']) for hit in hits]

        return entities
