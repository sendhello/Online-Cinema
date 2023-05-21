import asyncio
import json
import aiohttp
import pytest
import pytest_asyncio
import requests

from redis.asyncio import Redis
from elasticsearch import AsyncElasticsearch

from functional.settings import test_settings
from functional.testdata.es_mapping import index_to_schema
from functional.utils.models.base_models import HTTPResponse


@pytest_asyncio.fixture(scope='function')
async def es_client():
    url_elastic: str = test_settings.get_es_hosts()
    client = AsyncElasticsearch(hosts=url_elastic)
    yield client
    await client.close()
    es_delete_indexes(url_elastic, ['movies', 'persons', 'genre'])


def es_delete_indexes(url_elastic: str, indexes_names: list[str]) -> None:
    for index_name in indexes_names:
        requests.delete(f'{url_elastic}/{index_name}')


@pytest_asyncio.fixture(scope='function')
async def redis_client():
    redis_client_ = Redis(host=test_settings.redis_host, port=test_settings.redis_port)

    yield redis_client_
    await redis_client_.close()


@pytest_asyncio.fixture
async def session():
    session_ = aiohttp.ClientSession()
    yield session_
    await session_.close()


def get_es_bulk_query(es_data: list[dict], index_name: str, es_id_field: str):
    bulk_query = []
    for row in es_data:
        bulk_query.extend([
            json.dumps({
                'index': {
                    '_index': index_name,
                    '_id': row[es_id_field]
                }
            }),
            json.dumps(row)
        ])
    return bulk_query


@pytest.fixture
def es_write_data(es_client):
    async def inner(data: list[dict], es_index: str):
        bulk_query = get_es_bulk_query(data, es_index, test_settings.es_id_field)
        response = await es_client.bulk(operations=bulk_query, refresh=True)
        await asyncio.sleep(2)  # задержка для записи данных
        if response['errors']:
            raise Exception(f"Ошибка записи данных в Elasticsearch: {response}")

    return inner


@pytest.fixture
def service_get_data(session):
    async def inner(endpoint: str, params=None) -> HTTPResponse:
        if params is None:
            params = {}

        url = f"{test_settings.service_url}{endpoint}"
        async with session.get(url, params=params) as response:
            return HTTPResponse(
                body=await response.json(),
                status=response.status,
            )

    return inner


async def create_index(es_client):
    """Метод создает индексы для тестирования."""
    for index_name in ("movies", "genres", "persons"):
        if await es_client.indices.exists(index=index_name):
            await es_client.indices.delete(index=index_name)

        data_create_index = {
            "index": index_name,
            **index_to_schema.get(index_name)
        }
        await es_client.indices.create(
            **data_create_index
        )


def refactor(string: str) -> str:
    return string.replace("/", ".").replace("\\", ".").replace(".py", "")
