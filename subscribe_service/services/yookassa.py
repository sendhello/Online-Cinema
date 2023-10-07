from logging import getLogger

from fastapi import HTTPException
from starlette import status
from yookassa import Configuration
from yookassa import Payment as PaymentCreator
from yookassa import Refund
from yookassa.domain.response import PaymentResponse, RefundResponse

from constants import ExceptionText
from core.settings import settings
from schemas.payment import PaymentDBScheme
from schemas.yookassa import Amount, Confirmation, YookassaPayment, YookassaRefund
from services.base import BasePaymentMethodService


logger = getLogger(__name__)
Configuration.account_id = settings.yookassa.yookassa_shop_id
Configuration.secret_key = settings.yookassa.yookassa_api_key


class YookassaService(BasePaymentMethodService):
    def __init__(self, payment: PaymentDBScheme):
        self.payment = payment

    def send_payment(self) -> PaymentResponse:
        """Отправка платежа."""

        payment_params = YookassaPayment(
            amount=Amount(value=self.payment.amount),
            confirmation=Confirmation(
                return_url=settings.yookassa.yookassa_return_url.format(payment_id=str(self.payment.id))
            ),
            description=f"payment_id={self.payment.id}",
        )
        response = PaymentCreator.create(payment_params.dict(), idempotency_key=self.payment.id)
        response_data = response.json()
        logger.info(f"Yookassa payment response: {response_data}")
        return response

    def get_payment_status(self) -> PaymentResponse:
        """Проверка статуса платежа."""

        logger.debug(f"Try payment status by payment {self.payment.id} (remote_id={self.payment.remote_id})...")
        if self.payment.remote_id is None:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=ExceptionText.not_remote_id)

        response = PaymentCreator.find_one(str(self.payment.remote_id))
        response_data = response.json()
        logger.info(f"Yookassa payment response: {response_data}")
        return response

    def refund(self) -> RefundResponse:
        """Возврат платежа."""

        logger.debug(f"Try refund payment {self.payment.id} (remote_id={self.payment.remote_id})...")
        refund = YookassaRefund(
            amount=Amount(value=self.payment.amount),
            payment_id=str(self.payment.remote_id),
        )
        response_data = Refund.create(refund.dict())
        logger.info(f"Yookassa refund response: {response_data}")
        return response_data
