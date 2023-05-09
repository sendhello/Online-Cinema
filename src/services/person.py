from functools import lru_cache

from redis.asyncio import Redis
from elasticsearch import AsyncElasticsearch
from fastapi import Depends

from db.elastic import get_elastic
from db.redis import get_redis

from models.film import FilmShort
from api.schemas.person import PersonDescription
from services.base_entity import BaseEntity


class PersonService(BaseEntity):
    name = 'person'
    index_name = 'persons'

    def __init__(self, redis: Redis, elastic: AsyncElasticsearch):
        super().__init__(elastic, self.name, self.index_name)
        self.redis = redis

    async def get_persons(self, **kwargs):
        # todo добавить кэширование
        persons = await self.get_items_from_elastic(**kwargs)
        if not persons:
            return []
        return persons

    async def get_person_by_id(self, person_id):
        # todo добавить кэширование
        persons = await self._get_data_by_id_persons(person_id)
        if not persons:
            return []
        return persons

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
        movies_actor = [movie['_source']['id'] for movie in docs_actors['hits']['hits']]
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
        movies_writer = [movie['_source']['id'] for movie in docs_writes['hits']['hits']]
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
        movies_director = [movie['_source']['id'] for movie in docs_director['hits']['hits']]
        return count_movies_director, movies_director

    async def _get_data_by_id_persons(self, person_id: str):
        """Поиск по id по персонажам."""
        person = await self.elastic.get(index=self.index_name, id=person_id)
        full_name = person['_source']['full_name']

        count_movies_actor, movies_actor = await self._get_actors(person_id)
        count_movies_writers, movies_writer = await self._get_writers(person_id)
        count_movies_director, movies_director = await self._get_directors(full_name)

        person_films = []
        for movie_id in set(movies_actor + movies_writer + movies_director):
            person_films.append({'uuid': movie_id, 'roles': []})

            if movie_id in movies_actor:
                person_films[-1]['roles'].append('actor')

            if movie_id in movies_writer:
                person_films[-1]['roles'].append('writer')

            if movie_id in movies_director:
                person_films[-1]['roles'].append('director')

        return PersonDescription(
            **person['_source'],
            films=person_films
        )

    async def _get_person_film(self, person_id: str, role: str) -> list:
        body = {
            "query": {
                "nested": {
                    "path": role,
                    "query": {
                        "match": {
                            "actors.id": f"{person_id}"
                        }
                    }
                }
            }
        }
        docs: dict = await self.elastic.search(index=self.movies_index_name, body=body)
        return docs['hits'].get('hits')

    async def get_person_films_by_id(self, person_id: str) -> list[FilmShort]:
        films_info = []
        for role in ('actors', 'writers'):
            films_info.extend(await self._get_person_film(person_id, role))

        return [FilmShort(**movie['_source']) for movie in films_info]


@lru_cache()
def get_person_service(
        redis: Redis = Depends(get_redis),
        elastic: AsyncElasticsearch = Depends(get_elastic),
) -> PersonService:
    return PersonService(redis, elastic)
