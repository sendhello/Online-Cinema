import asyncio
import json
import logging
from contextlib import asynccontextmanager

from constants import NotificationStatus, TaskType
from core.settings import settings
from gateways.auth import auth_gateway
from gateways.notification_api import notification_api_gateway
from gateways.rabbitmq import RabbitGateway
from schemas.message import EmailScheme


logger = logging.getLogger(settings.project_name)


@asynccontextmanager
async def rabbit_gateway_manager():
    rabbit_gateway = RabbitGateway()
    await rabbit_gateway.startup()
    yield rabbit_gateway

    await rabbit_gateway.shutdown()


async def main():
    async with rabbit_gateway_manager() as rabbit_gateway:
        while True:
            await asyncio.sleep(settings.request_period)

            try:
                new_notifications = await notification_api_gateway.get_new_notifications()
            except Exception as e:
                logger.error(f"Notification API request error: {e}")
                continue

            if not new_notifications:
                continue

            try:
                access_token = await auth_gateway.login()
            except Exception as e:
                logger.error(f"Auth request error: {e}")
                continue

            for notification in new_notifications:
                if notification.type != TaskType.EMAIL:
                    continue

                try:
                    user = await auth_gateway.get_user_data(user_id=notification.user_id, access_token=access_token)
                except Exception as e:
                    logger.error(f"Get user {notification.user_id} error: {e}")
                    notification_status = NotificationStatus.ERROR
                else:
                    notification_status = NotificationStatus.PROCESSING
                    email = EmailScheme(notification_id=notification.id, email=user.email, body=notification.content)
                    await rabbit_gateway.send_data_in_queue(
                        queue_name=settings.rabbitmq_send_queue_name,
                        data=json.loads(email.json()),
                    )

                await notification_api_gateway.set_notification_status(notification.id, notification_status)


if __name__ == "__main__":
    asyncio.run(main())
