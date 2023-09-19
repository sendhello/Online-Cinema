import logging

from constants import NotificationStatus
from core.settings import settings
from gateways.base import BaseAsyncGateway
from schemas.notification import NotificationScheme


logger = logging.getLogger(settings.project_name)


class NotificationApiGateway(BaseAsyncGateway):
    async def get_new_notifications(self) -> list[NotificationScheme]:
        response = await self._client.get("/api/v1/notification/", params={"status": "created", "need_send": True})
        response.raise_for_status()
        return [NotificationScheme.parse_obj(raw_message) for raw_message in response.json()]

    async def set_notification_status(self, message_id, status: NotificationStatus) -> None:
        response = await self._client.patch(f"/api/v1/notification/{message_id}", json={"status": status})
        response.raise_for_status()


notification_api_gateway = NotificationApiGateway(
    base_url=settings.notification_api_gateway,
)
