import json

from aio_pika import IncomingMessage
from logging import getLogger
from core.settings import settings
from schemas.email_status import EmailStatus
from pydantic import ValidationError
from services.email import email_service

from schemas.message import EmailScheme


logger = getLogger(settings.project_name)


def rmq_handler_wrapper(rabbit_gateway):
    async def rmq_handler(message: IncomingMessage) -> None:
        message_content = message.body.decode("utf-8")

        try:
            email = EmailScheme.parse_raw(message_content)
            await message.ack()

        except json.JSONDecodeError as exc:
            logger.error(f"Unable to parse message: {str(exc)}")
            await message.ack()
            return None

        except ValidationError as exc:
            error_message = f"Request body content error. {str(exc.errors())}"
            logger.error(error_message)
            await message.ack()
            return None

        except Exception as ex:
            error_message = f"Handler error. Type error: {type(ex)=}, message: {str(ex)}"
            logger.error(error_message)
            await message.ack()
            return None

        is_sent, error_message = email_service.send_message(message=email)
        email_status = EmailStatus.create(email, is_sent, error_message)
        await rabbit_gateway.send_data_in_queue(
            queue_name=settings.rabbitmq_send_queue_name,
            data=json.loads(email_status.json()),
        )

    return rmq_handler
