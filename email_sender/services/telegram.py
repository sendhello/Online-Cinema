import logging

from services.abstract_message import AbstractMessageService
from schemas.base import Model

logger = logging.getLogger(__name__)


class TelegramService(AbstractMessageService):
    def send_message(self, message: Model):
        print(f"Message {message} is sent via SMS.")
