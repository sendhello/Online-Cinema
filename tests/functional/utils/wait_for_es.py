import asyncio
from elasticsearch import AsyncElasticsearch
from functional.settings import test_settings, SLEEP_TIME


async def wait_for_es(sleep_time: int = 2):
    es_client = AsyncElasticsearch(hosts=test_settings.get_es_hosts())

    while True:
        if await es_client.ping():
            break
        await asyncio.sleep(sleep_time)

if __name__ == '__main__':
    asyncio.run(wait_for_es(sleep_time=SLEEP_TIME))
