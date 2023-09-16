import logging

from core.settings import settings
from gateways.base import BaseAsyncGateway


logger = logging.getLogger(settings.project_name)


class NotificationApiGateway(BaseAsyncGateway):
    async def get_new_messages(self) -> dict | None:
        response = await self._client.get("/api/v1/notification/", params={"status": "created", "need_send": True})
        response.raise_for_status()
        return response.json()


notification_api_gateway = NotificationApiGateway(
    base_url=settings.notification_api_gateway,
)
