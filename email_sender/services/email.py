import logging
import smtplib

from core.settings import settings
from schemas.message import EmailScheme
from services.abstract_message import AbstractMessageService
from email.message import Message

logger = logging.getLogger(__name__)


class EmailService(AbstractMessageService):
    def __init__(self, smtp_host: str, smtp_port: int):
        self.smtp_server = smtplib.SMTP(smtp_host, smtp_port)
        self.smtp_server.set_debuglevel(True)

    @staticmethod
    def _create_msg(message: EmailScheme) -> Message:
        msg = Message()
        msg["From"] = f"{message.from_name} <{message.from_email}>"
        msg["To"] = message.email
        msg["Subject"] = message.subject
        msg.set_payload(message.body)
        msg.set_charset("utf-8")
        return msg

    def send_message(self, message: EmailScheme):
        try:
            self.smtp_server.send_message(self._create_msg(message))

        except smtplib.SMTPException as exc:
            reason = f"Message {message.notification_id} was not sent. {type(exc).__name__}: {exc}"
            logging.error(reason)
            return False, reason

        logging.info(f"Message {message.notification_id} is sent.")
        return True, None


email_service = EmailService(settings.smtp_host, settings.smtp_port)
