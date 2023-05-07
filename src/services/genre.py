from functools import lru_cache
from typing import Optional

from redis.asyncio import Redis
from elasticsearch import AsyncElasticsearch, NotFoundError
from fastapi import Depends

from db.elastic import get_elastic
from db.redis import get_redis
from models.film import Genre
from constants import GenreSort


class GenreService:
    index_name = 'genres'

    def __init__(self, redis: Redis, elastic: AsyncElasticsearch):
        self.redis = redis
        self.elastic = elastic

    async def get_genre_by_id(self, genre_id):
        # todo добавить кэширование
        genres = await self._get_genre_from_elastic(genre_id)
        if not genres:
            return []
        return genres

    async def get_genres(self, **kwargs):
        # todo добавить кэширование
        genres = await self._get_genres_from_elastic(**kwargs)
        if not genres:
            return []
        return genres

    @staticmethod
    async def _transform_doc_to_genre(doc: dict) -> Genre:
        genre = doc['_source'].get('genre')
        if genre:
            doc['_source']['genre'] = [{'id': item, 'name': item} for item in genre.split(' ')]
        result = Genre(**doc['_source'])
        return result

    async def _get_genre_from_elastic(self, genre_id: str) -> Optional[Genre]:
        try:
            doc = await self.elastic.get(index=self.index_name, id=genre_id)
        except NotFoundError:
            return

        genre = doc['_source'].get('genre')
        if genre and isinstance(genre, str):
            doc['_source']['genre'] = [{'id': item, 'name': item} for item in genre.split(' ')]
        return Genre(**doc['_source'])

    @staticmethod
    def _get_genre_body(
            query: str | None = None,
            genre_id: str | None = None
    ) -> dict | None:

        if genre_id:
            return {
                'query': {
                    'query_string': {
                        'default_field': 'genre',
                        'query': genre_id
                    }
                }
            }

        if query:
            return {
                'query': {
                    'match': {
                        'name': {
                            'query': query,
                            'fuzziness': 1,
                            'operator': 'and',
                            'analyzer': 'ru_en'
                        }
                    }
                }
            }

    async def _get_genres_from_elastic(
            self,
            page_size: int | None,
            page_number: int | None,
            sort: GenreSort | None = None,
            genre_id: str | None = None,
            query: str | None = None,
    ) -> Optional[list[Genre]]:

        body = self._get_genre_body(query, genre_id)

        match sort:
            case GenreSort.ID_UP:
                sort = [{"id": "asc"}]
            case GenreSort.ID_DOWN:
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

        return [await self._transform_doc_to_genre(doc) for doc in docs['hits']['hits']]


@lru_cache()
def get_genre_service(
        redis: Redis = Depends(get_redis),
        elastic: AsyncElasticsearch = Depends(get_elastic),
) -> GenreService:
    return GenreService(redis, elastic)
