from socket import AF_INET
from typing import Optional

import aiohttp
from fastapi.logger import logger


SIZE_POOL_AIOHTTP = 100


class AiohttpClient:
    session: Optional[aiohttp.ClientSession] = None

    @classmethod
    def get_session(cls) -> aiohttp.ClientSession:
        if cls.session is None:
            timeout = aiohttp.ClientTimeout(total=2)
            connector = aiohttp.TCPConnector(
                family=AF_INET, limit_per_host=SIZE_POOL_AIOHTTP
            )
            cls.session = aiohttp.ClientSession(timeout=timeout, connector=connector)

        return cls.session

    @classmethod
    async def close_session(cls) -> None:
        if cls.session:
            await cls.session.close()
            cls.session = None

    @classmethod
    async def query_url(
        cls, url: str, params: dict = None, headers: dict = None
    ) -> tuple[int, dict]:
        session = cls.get_session()
        try:
            async with session.get(url, params=params, headers=headers) as response:
                status = response.status
                json_result = await response.json()

        except Exception as e:
            status = 500
            logger.error(f'Request error: {e}')
            return status, {}

        return status, json_result
