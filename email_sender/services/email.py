import logging
import smtplib

from core.settings import settings
from schemas.message import EmailScheme
from services.abstract_message import AbstractMessageService

logger = logging.getLogger(__name__)


class EmailService(AbstractMessageService):
    def __init__(self, smtp_host: str, smtp_port: int):
        self.smtp_server = smtplib.SMTP(smtp_host, smtp_port)
        self.smtp_server.set_debuglevel(True)

    def send_message(self, message: EmailScheme):
        try:
            self.smtp_server.sendmail(
                from_addr=message.from_email,
                to_addrs=message.email,
                msg=message.body,
            )

        except smtplib.SMTPException as exc:
            reason = f"Message {message.notification_id} was not sent. {type(exc).__name__}: {exc}"
            logging.error(reason)
            return False, reason

        logging.info(f"Message {message.notification_id} is sent.")
        return True, None


email_service = EmailService(settings.smtp_host, settings.smtp_port)
