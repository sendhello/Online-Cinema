import asyncio
import json
import logging
from contextlib import asynccontextmanager

from core.settings import settings
from gateways.rabbitmq import RabbitGateway
from schemas.message import EmailScheme
from handlers.rabbitmq import rmq_handler_wrapper


logger = logging.getLogger(settings.project_name)


@asynccontextmanager
async def rabbit_gateway_manager():
    rabbit_gateway = RabbitGateway()
    await rabbit_gateway.startup()
    await rabbit_gateway.create_queue_listener(
        queue_name=settings.rabbitmq_source_queue_name,
        callback_worker=rmq_handler_wrapper(rabbit_gateway),
    )
    yield rabbit_gateway

    await rabbit_gateway.shutdown()


async def main():
    logger.info("Email Sender is started.")
    async with rabbit_gateway_manager():
        await asyncio.sleep(3600)


if __name__ == "__main__":
    asyncio.run(main())
