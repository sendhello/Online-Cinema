import asyncio
import logging
from typing import Callable

from httpx import HTTPStatusError

from core.settings import settings
from gateways.auth import auth_gateway
from gateways.notification_api import notification_api_gateway
from gateways.subscribe_service import subscribe_service_gateway
from services.subscribe import SubscribeService


logger = logging.getLogger(settings.project_name)


async def run(task: Callable):
    """Обертка для запуска задач."""

    logger.debug(f"Start task {task.__name__}")
    try:
        await task()

    except HTTPStatusError as e:
        if e.response.status_code != 422:
            logger.error(f"Error task {task.__name__}: {e}", exc_info=True)
            return None

        try:
            await task(update_token=True)
        except Exception as e:
            logger.error(f"Error task {task.__name__}: {e}", exc_info=True)

    except Exception as e:
        logger.error(f"Error task {task.__name__}: {e}", exc_info=True)

    logger.debug(f"Success task {task.__name__}")


async def main():
    while True:
        await asyncio.sleep(settings.request_period)

        service = SubscribeService(
            auth_gateway=auth_gateway,
            subscribe_service_gateway=subscribe_service_gateway,
            notification_api_gateway=notification_api_gateway,
        )
        await run(service.update_pending_payments)
        await run(service.update_pending_subscribes)
        await run(service.update_expired_subscribes)


if __name__ == "__main__":
    asyncio.run(main())
