import asyncio

import backoff
from elasticsearch import AsyncElasticsearch, ConnectionError
from functional.settings import backoff_settings, test_settings


@backoff.on_exception(
    **backoff_settings.dict(),
    exception=ConnectionError,
)
async def wait_for_es():
    es_client = AsyncElasticsearch(hosts=test_settings.get_es_hosts())

    if not await es_client.ping():
        raise ConnectionError('Connect to elasticsearch is failed.')
    return es_client

if __name__ == '__main__':
    asyncio.run(wait_for_es())
