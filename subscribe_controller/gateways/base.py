import logging
from abc import ABC
from http import HTTPStatus

import httpx

from core.settings import settings


logger = logging.getLogger(settings.project_name)


class BaseAsyncGateway(ABC):
    def __init__(self, base_url: str, headers=None, log_body: bool = False, **kwargs):
        self.BASE_URL = base_url
        self._client = httpx.AsyncClient(
            base_url=self.BASE_URL,
            headers=headers,
            event_hooks={"response": [self.log_response_with_body if log_body else self.log_response]},
            timeout=30,
            **kwargs,
        )

    async def close(self):
        await self._client.aclose()

    @classmethod
    async def log_response(cls, response: httpx.Response):
        await response.aread()
        logger.info(cls._get_ok_response_log(response))
        if response.status_code >= HTTPStatus.BAD_REQUEST:
            logger.error(cls._get_bad_request_log(response))

    @classmethod
    async def log_response_with_body(cls, response: httpx.Response):
        await response.aread()
        logger.info(cls._get_ok_response_log(response) + cls._get_ok_response_body_log(response))
        if response.status_code >= HTTPStatus.BAD_REQUEST:
            logger.error(cls._get_bad_request_log(response))

    @staticmethod
    def _get_bad_request_log(response: httpx.Response):
        return (
            f'Request — "{response.request.method} {response.url}" '
            f"{response.status_code} {response.reason_phrase}\n"
            f"{response.text}"
        )

    @staticmethod
    def _get_ok_response_log(response: httpx.Response):
        return (
            f'Request — "{response.request.method} {response.url}" ' f"{response.status_code} {response.reason_phrase}"
        )

    @staticmethod
    def _get_ok_response_body_log(response: httpx.Response):
        return (
            f"\nRequest Body:\n"
            f"{response.request.content if len(response.request.content) else '<empty body>'}\n"
            f"Response Body:\n"
            f"{response.text or '<empty body>'}"
        )
