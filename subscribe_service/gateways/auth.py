import logging

from core.settings import settings
from gateways.base import BaseAsyncGateway


logger = logging.getLogger(settings.project_name)


class AuthGateway(BaseAsyncGateway):
    async def validate(self, authorization) -> dict:
        response = await self._client.get("/api/v1/verify/token", headers={"Authorization": authorization})
        response.raise_for_status()
        return response.json()


auth_gateway = AuthGateway(
    base_url=settings.auth_gateway,
)
