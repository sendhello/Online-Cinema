import asyncio
import backoff

from redis.asyncio import Redis
from redis.exceptions import ConnectionError
from functional.settings import test_settings, backoff_settings


@backoff.on_exception(
    **backoff_settings.dict(),
    exception=ConnectionError,
)
async def wait_for_redis():
    redis_client = await Redis(host=test_settings.redis_host, port=test_settings.redis_port)

    if not await redis_client.ping():
        raise ConnectionError
    return redis_client


if __name__ == '__main__':
    asyncio.run(wait_for_redis())
