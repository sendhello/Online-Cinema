from logging import getLogger
from uuid import uuid4

from yookassa import Configuration
from yookassa import Payment as PaymentCreator
from yookassa.domain.response import PaymentResponse

from core.settings import settings
from schemas.payment import PaymentDBScheme
from schemas.yookassa import Amount, Confirmation, YookassaPayment
from services.base import BasePaymentMethodService


logger = getLogger(__name__)
Configuration.account_id = settings.yookassa_shop_id
Configuration.secret_key = settings.yookassa_api_key


class YookassaService(BasePaymentMethodService):
    def __init__(self, payment: PaymentDBScheme):
        self.payment = payment

    def send_payment(self) -> PaymentResponse:
        """Отправка платежа."""

        payment_params = YookassaPayment(
            amount=Amount(value=self.payment.amount),
            confirmation=Confirmation(return_url=settings.yookassa_return_url),
            description=f"payment_id={self.payment.id}",
        )
        response = PaymentCreator.create(payment_params.dict(), idempotency_key=uuid4())
        response_data = response.json()
        logger.info(f"Yookassa payment response: {response_data}")
        return response

    def get_payment_status(self) -> PaymentResponse:
        """Проверка статуса платежа."""

        logger.debug(f"Try payment status by payment {self.payment.id} (remote_id={self.payment.remote_id})...")
        if self.payment.remote_id is None:
            raise ValueError("Payment don't have 'remote_id'")

        response = PaymentCreator.find_one(str(self.payment.remote_id))
        response_data = response.json()
        logger.info(f"Yookassa payment response: {response_data}")
        return response
