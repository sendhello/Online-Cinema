import asyncio
import json
import aiohttp
import pytest
import pytest_asyncio

from redis.asyncio import Redis
from elasticsearch import AsyncElasticsearch

from functional.settings import test_settings
from functional.testdata.es_mapping import index_to_schema
from functional.utils.models.base_models import HTTPResponse


INDEX_NAMES = index_to_schema.keys()


async def _create_index(es_client: AsyncElasticsearch):
    """Метод создает индексы для тестирования."""
    for index_name in INDEX_NAMES:
        if await es_client.indices.exists(index=index_name):
            await es_client.indices.delete(index=index_name)

        data_create_index = {
            "index": index_name,
            **index_to_schema.get(index_name)
        }
        await es_client.indices.create(
            **data_create_index
        )


async def _delete_index(es_client: AsyncElasticsearch) -> None:
    """Удаление индексов.
    """
    for index_name in INDEX_NAMES:
        if not await es_client.indices.exists(index=index_name):
            continue

        await es_client.indices.delete(index=index_name)


def _get_es_bulk_query(es_data: list[dict], index_name: str, es_id_field: str):
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


@pytest_asyncio.fixture(scope='function')
async def es_client():
    client = AsyncElasticsearch(hosts=test_settings.get_es_hosts())
    await _create_index(client)
    yield client

    await _delete_index(client)
    await client.close()


@pytest_asyncio.fixture
def es_write_data(es_client: AsyncElasticsearch):
    async def inner(data: list[dict], es_index: str):
        bulk_query = _get_es_bulk_query(data, es_index, test_settings.es_id_field)
        response = await es_client.bulk(operations=bulk_query, refresh=True)
        await asyncio.sleep(2)  # задержка для записи данных

        if response['errors']:
            raise Exception(f"Ошибка записи данных в Elasticsearch: {response}")

    return inner


@pytest_asyncio.fixture(scope='function')
async def redis_client():
    redis = Redis(host=test_settings.redis_host, port=test_settings.redis_port)
    await redis.flushall()
    yield redis

    await redis.close()


@pytest_asyncio.fixture
async def session():
    session_ = aiohttp.ClientSession()
    yield session_

    await session_.close()


@pytest_asyncio.fixture
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
