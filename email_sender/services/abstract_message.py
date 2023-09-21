from abc import ABC, abstractmethod

from schemas.base import Model


class AbstractMessageService(ABC):
    @abstractmethod
    def send_message(self, message: Model):
        ...
