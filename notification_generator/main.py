import asyncio
from contextlib import asynccontextmanager
import logging
from core.settings import settings
from gateways.notification_api import notification_api_gateway
from gateways.rabbitmq import RabbitGateway


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
            try:
                new_messages = await notification_api_gateway.get_new_messages()

            except Exception as e:
                logger.error(f"Request error: {e}")
                await asyncio.sleep(settings.request_period)
                continue

            for message in new_messages:
                await rabbit_gateway.send_data_in_queue(
                    data=message,
                    queue_name=settings.rabbitmq_send_queue_name,
                )

            await asyncio.sleep(settings.request_period)


if __name__ == "__main__":
    asyncio.run(main())
