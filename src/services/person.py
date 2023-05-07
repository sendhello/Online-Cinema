import logging
from functools import lru_cache
from typing import Optional

from redis.asyncio import Redis
from elasticsearch import AsyncElasticsearch, NotFoundError
from fastapi import Depends

from db.elastic import get_elastic
from db.redis import get_redis
from models.film import Person, FilmShort
from constants import PersonSort


class PersonService:
    index_name = 'persons'
    movies_index_name = 'movies'

    def __init__(self, redis: Redis, elastic: AsyncElasticsearch):
        self.redis = redis
        self.elastic = elastic

    async def get_persons(self, **kwargs):
        # todo добавить кэширование
        persons = await self._get_persons_from_elastic(**kwargs)
        if not persons:
            return []
        return persons

    async def get_person_by_id(self, person_id):
        # todo добавить кэширование
        persons = await self._get_data_by_id_persons(person_id)
        if not persons:
            return []
        return persons

    @staticmethod
    async def _transform_doc_to_person(doc: dict) -> Person:
        person = doc['_source'].get('person')
        if person:
            doc['_source']['person'] = [{'id': item, 'full_name': item} for item in person.split(' ')]
        logging.info(f"privet {doc}")
        result = Person(**doc['_source'])
        return result

    async def _get_actors(self, person_id: str):
        body_actor = {
            "query": {
                "nested": {
                    "path": "actors",
                    "query": {
                        "match": {
                            "actors.id": f"{person_id}"
                        }
                    }
                }
            }
        }
        docs_actors = await self.elastic.search(index=self.movies_index_name, body=body_actor)
        count_movies_actor = docs_actors['hits']['total']['value']
        movies_actor = [(movie['_source']['id'], movie['_source']['title']) for movie in docs_actors['hits']['hits']]
        return count_movies_actor, movies_actor

    async def _get_writers(self, person_id: str):
        body_writer = {
            "query": {
                "nested": {
                    "path": "writers",
                    "query": {
                        "match": {
                            "writers.id": f"{person_id}"
                        }
                    }
                }
            }
        }
        docs_writes = await self.elastic.search(index="movies", body=body_writer)
        count_movies_writers = docs_writes['hits']['total']['value']
        movies_writer = [(movie['_source']['id'], movie['_source']['title']) for movie in docs_writes['hits']['hits']]
        return count_movies_writers, movies_writer

    async def _get_directors(self, full_name: str):
        body_director = {
            "query": {
                "match": {
                    "director": f"{full_name}"
                }
            }
        }
        docs_director = await self.elastic.search(index="movies", body=body_director)
        count_movies_director = docs_director['hits']['total']['value']
        movies_director = [(movie['_source']['id'], movie['_source']['title']) for movie in docs_director['hits']['hits']]
        return count_movies_director, movies_director

    async def _get_data_by_id_persons(self, person_id: str):
        """Поиск по id по персонажам."""
        person = await self.elastic.get(index=self.index_name, id=person_id)
        full_name = person['_source']['full_name']

        count_movies_actor, movies_actor = await self._get_actors(person_id)
        count_movies_writers, movies_writer = await self._get_writers(person_id)
        count_movies_director, movies_director = await self._get_directors(full_name)
        data = {}

        for role, films_info in zip(
            ('actor', 'writer', 'director'),
            (movies_actor, movies_writer, movies_director)
        ):

            for film_info in films_info:
                logging.info(f"LOOOOOL {film_info}")
                film_id, film_title = film_info
                if film_id in data:
                    data[film_id]['roles'].append(role)
                else:
                    data[film_id] = {'title': [], 'roles': []}
                    data[film_id]['title'] = film_title
                    data[film_id]['roles'] = [role]

        return dict(
            **person['_source'],
            data=data
        )

    async def _get_person_from_elastic(self, person_id: str) -> Optional[Person]:
        try:
            doc = await self.elastic.get(index=self.index_name, id=person_id)
        except NotFoundError:
            return

        person = doc['_source'].get('person')
        if person and isinstance(person, str):
            doc['_source']['person'] = [{'id': item, 'full_name': item} for item in person.split(' ')]
        # return Person(**doc['_source'].dict(by_alias=True))
        return Person(**doc['_source'])

    @staticmethod
    def _get_person_body(
            query: str | None = None,
            person_id: str | None = None
    ) -> dict | None:
        # todo utils
        if person_id:
            return {
                'query': {
                    'query_string': {
                        'default_field': 'person',
                        'query': person_id
                    }
                }
            }

        if query:
            return {
                'query': {
                    'match': {
                        'full_name': {
                            'query': query,
                            'fuzziness': 1,
                            'operator': 'and',
                            'analyzer': 'ru_en'
                        }
                    }
                }
            }

    async def get_persons_film_by_id(self, person_id: str) -> list[FilmShort]:
        body = {
            "query": {
                "nested": {
                    "path": "actors",
                    "query": {
                        "match": {
                            "actors.id": f"{person_id}"
                        }
                    }
                }
            }
        }
        docs_actors = await self.elastic.search(index="movies", body=body)
        logging.info(f"paket {[FilmShort(**movie['_source']) for movie in docs_actors['hits']['hits']]}")
        return [FilmShort(**movie['_source']) for movie in docs_actors['hits']['hits']]

    async def _get_persons_from_elastic(
            self,
            page_size: int | None,
            page_number: int | None,
            sort: PersonSort | None = None,
            person_id: str | None = None,
            query: str | None = None,
    ) -> Optional[list[Person]]:

        body = self._get_person_body(query, person_id)

        match sort:
            case PersonSort.ID_UP:
                sort = [{"id": "asc"}]
            case PersonSort.ID_DOWN:
                sort = [{"id": "desc"}]
            case _:
                sort = []
        sort.append({"_score": "desc"})

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

        return [await self._transform_doc_to_person(doc) for doc in docs['hits']['hits']]


@lru_cache()
def get_person_service(
        redis: Redis = Depends(get_redis),
        elastic: AsyncElasticsearch = Depends(get_elastic),
) -> PersonService:
    return PersonService(redis, elastic)
