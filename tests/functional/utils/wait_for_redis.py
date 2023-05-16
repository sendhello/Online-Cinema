import asyncio
from redis.asyncio import Redis
from functional.settings import test_settings, SLEEP_TIME


async def wait_for_es(sleep_time: int = 2):
    redis_client = Redis(host=test_settings.redis_host, port=test_settings.redis_port)

    while True:
        if redis_client.ping():
            break
        await asyncio.sleep(sleep_time)

if __name__ == '__main__':
    asyncio.run(wait_for_es(sleep_time=SLEEP_TIME))
