import json

from aio_pika import IncomingMessage
from pydantic import ValidationError

from constants import NotificationStatus
from core.get_logger import get_logger
from db.postgres import async_session
from schemas.email_status import EmailStatus
from services.notification import NotificationService


logger = get_logger()


async def rmq_handler(message: IncomingMessage) -> None:
    message_content = message.body.decode("utf-8")

    try:
        email_status = EmailStatus.parse_raw(message_content)
        notification_status = NotificationStatus.COMPLETED if email_status.ok else NotificationStatus.ERROR

        async with async_session() as session:
            service = NotificationService(session)
            is_processed = await service.set_status(
                email_status.notification_id, notification_status, email_status.request_id
            )

            if is_processed:
                await message.ack()
            else:
                await message.reject()

    except json.JSONDecodeError as exc:
        logger.error(f"Unable to parse message: {str(exc)}")
        await message.ack()

    except ValidationError as exc:
        error_message = f"Request body content error. {str(exc.errors())}"
        logger.error(error_message)
        await message.ack()

    except Exception as ex:
        error_message = f"Handler error. Type error: {type(ex)=}, message: {str(ex)}"
        logger.error(error_message)
        await message.ack()
