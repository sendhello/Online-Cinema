from abc import ABC, abstractmethod


class BasePaymentMethodService(ABC):
    @abstractmethod
    def send_payment(self):
        """Отправка платежа."""
        ...

    @abstractmethod
    def get_payment_status(self):
        """Проверка статуса платежа."""
        ...
