from functools import lru_cache

import orjson
from elasticsearch import AsyncElasticsearch
from fastapi import Depends
from redis.asyncio import Redis

from db.elastic import get_elastic
from db.redis import get_redis

from models.film import FilmShort
from models.person import Person, PersonDescription, PersonFilm
from services.base_entity import BaseEntity


class PersonService(BaseEntity):
    name = 'person'
    index_name = 'persons'

    def __init__(self, redis: Redis, elastic: AsyncElasticsearch):
        super().__init__(
            redis=redis,
            elastic=elastic,
            entity_name=self.name,
            index_name=self.index_name
        )

    async def get_persons(self, **kwargs):
        key = f"persons:{'-'.join(str(val) for val in kwargs.values())}"
        persons = await self._get_persons_from_cache(key)

        if not persons:
            persons = await self.get_items_from_elastic(**kwargs)

            await self._put_persons_to_cache(key, persons)

        return persons

    async def get_person_by_id(self, person_id):
        person = await self._get_person_from_cache(person_id)

        if not person:
            person = await self._get_data_by_id_persons(person_id)
            if not person:
                return None

            await self._put_person_to_cache(person)

        return person

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
            person_films[-1] = PersonFilm(**person_films[-1])
        return PersonDescription(
            **person['_source'],
            films=person_films
        )

    async def _get_person_film(self, person_id: str, role: str) -> list[FilmShort]:
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
        hits = docs['hits'].get('hits')
        return [FilmShort(**hit['_source']) for hit in hits]

    async def get_persons_films_from_es(self, person_id: str) -> list[FilmShort]:
        films = []
        for role in ('actors', 'writers'):
            films.extend(await self._get_person_film(person_id, role))
        return films

    async def get_person_films_by_id(self, person_id: str) -> list[FilmShort]:
        key = f"person_films:{person_id}"
        films = await self._get_films_from_cache(key)

        if not films:
            films = await self.get_persons_films_from_es(person_id)

        await self._put_films_to_cache(key, films=films)

        return films

    async def _put_person_to_cache(self, person: Person | PersonDescription):
        key = f'person:{person.uuid}'
        await self._put_to_cache(key, person.json(by_alias=True))

    async def _put_persons_to_cache(self, key, persons: list[Person]):
        data = [person.dict(by_alias=True) for person in persons]
        await self._put_to_cache(key, orjson.dumps(data))

    async def _put_films_to_cache(self, key, films: list[FilmShort]):
        data = [film.dict(by_alias=True) for film in films]
        await self._put_to_cache(key, orjson.dumps(data))

    async def _get_person_from_cache(self, person_id: str) -> Person | None:
        key = f'person:{person_id}'
        data = await self._get_from_cache(key)
        if data is None:
            return None

        person = Person.parse_raw(data)
        return person

    async def _get_persons_from_cache(self, key) -> list[Person] | None:
        data = await self._get_from_cache(key)
        if data is None:
            return None

        persons = [Person.parse_obj(person_raw) for person_raw in orjson.loads(data)]
        return persons

    async def _get_films_from_cache(self, key) -> list[FilmShort] | None:
        data = await self._get_from_cache(key)
        if data is None:
            return None

        films = [FilmShort.parse_obj(person_raw) for person_raw in orjson.loads(data)]
        return films


@lru_cache()
def get_person_service(
        redis: Redis = Depends(get_redis),
        elastic: AsyncElasticsearch = Depends(get_elastic),
) -> PersonService:
    return PersonService(redis, elastic)
