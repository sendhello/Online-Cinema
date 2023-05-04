import pickle
from functools import lru_cache
from http import HTTPStatus
from typing import Optional
from uuid import UUID

import jmespath
from elasticsearch import AsyncElasticsearch, BadRequestError, NotFoundError
from fastapi import Depends, HTTPException
from redis.asyncio import Redis

from constants import FILM_CACHE_EXPIRE_IN_SECONDS, FilmSort
from db.elastic import get_elastic
from db.redis import get_redis
from models.film import Film


class FilmService:
    def __init__(self, redis: Redis, elastic: AsyncElasticsearch):
        self.redis = redis
        self.elastic = elastic

    async def filter(
            self,
            page_size: int,
            page_number: int,
            sort: FilmSort | None = None,
            genre: str | None = None,
            query: str | None = None,
    ) -> list[Film]:
        # TODO: реализовать кеширование
        # films = await self._films_from_cache()
        films = None  # заглушка

        if not films:
            films = await self._get_films_from_elastic(
                film_sort=sort,
                genre=genre,
                text_query=query,
                size=page_size,
                page_number=page_number,
            )

            # await self._put_films_to_cache(films)

        return films

    async def get_by_id(self, film_id: str) -> Optional[Film]:
        film = await self._film_from_cache(film_id)

        if not film:
            film = await self._get_film_from_elastic(film_id)
            if not film:
                return None

            await self._put_film_to_cache(film)

        return film

    async def _get_film_from_elastic(self, film_id: str) -> Optional[Film]:
        try:
            doc = await self.elastic.get(index='movies', id=film_id)

        except NotFoundError:
            return None

        return Film(**doc['_source'])

    async def _get_films_from_elastic(
            self,
            film_sort: FilmSort | None,
            genre: str | None,
            text_query: str | None,
            size: int,
            page_number: int,
    ) -> list[Film]:
        if genre is None and text_query is None:
            query = {'match_all': {}}
        else:
            query = {
                "bool": {
                    "must": []
                }
            }

            if genre is not None:
                query['bool']['must'].append({'match': {'genre': genre}})

            if text_query is not None:
                query['bool']['must'].append(
                    {
                        'multi_match': {
                            "query": text_query,
                            "fields": ['title', 'description', 'actors_names', 'director', 'writers_names', 'genre'],
                            "fuzziness": "auto"
                        }
                    }
                )

        match film_sort:
            case FilmSort.RATING_UP:
                sort = [{"imdb_rating": "asc"}]
            case FilmSort.RATING_DOWN:
                sort = [{"imdb_rating": "desc"}]
            case _:
                sort = []

        sort.append({"_score": "desc"})

        try:
            response = await self.elastic.search(
                index='movies',
                query=query,
                sort=sort,
                size=size,
                from_=(page_number - 1) * size
            )
        except BadRequestError as e:
            error_message = jmespath.search('error.root_cause[0].reason', e.body)
            raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail=error_message)

        hits = response.get('hits', {}).get('hits', [])
        films = [Film(**hit['_source']) for hit in hits]

        return films

    async def _film_from_cache(self, film_id: str) -> Optional[Film]:
        data = await self.redis.get(film_id)
        if not data:
            return None

        # pydantic предоставляет удобное API для создания объекта моделей из json
        film = Film.parse_raw(data)
        return film

    async def _films_from_cache(self) -> list[Film]:
        data = await self.redis.get('all_movies')
        if not data:
            return []

        films = [Film.parse_obj(film_raw) for film_raw in pickle.loads(data)]
        return films

    async def _put_film_to_cache(self, film: Film):
        await self.redis.set(film.uuid, film.json(), FILM_CACHE_EXPIRE_IN_SECONDS)

    async def _put_films_to_cache(self, films: list[Film]):
        await self.redis.set('all_films', pickle.dumps([film.dict() for film in films]), FILM_CACHE_EXPIRE_IN_SECONDS)


@lru_cache()
def get_film_service(
        redis: Redis = Depends(get_redis),
        elastic: AsyncElasticsearch = Depends(get_elastic),
) -> FilmService:
    return FilmService(redis, elastic)
