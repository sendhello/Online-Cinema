import logging
from datetime import datetime
from uuid import UUID

from core.settings import settings
from gateways.base import BaseAsyncGateway
from schemas.notification import NotificationScheme


logger = logging.getLogger(settings.project_name)


class NotificationApiGateway(BaseAsyncGateway):
    async def send_email(self, user_id: UUID, message: str) -> NotificationScheme:
        logger.debug("Try send emails...")
        response = await self._client.post(
            "/api/v1/task/",
            json={
                "content": message,
                "type": "email",
                "user_ids": [str(user_id)],
                "send_to": datetime.utcnow().isoformat(),
            },
        )
        logger.debug(f"Emails sent with code {response.status_code}")
        response.raise_for_status()
        logger.info(f"Message '{message}' sent to user {user_id}.")
        logger.debug(f"Emails sent: {response.json()}")
        return NotificationScheme.parse_obj(response.json())


notification_api_gateway = NotificationApiGateway(
    base_url=settings.notification_api_gateway,
)
