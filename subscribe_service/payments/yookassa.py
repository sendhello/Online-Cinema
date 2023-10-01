from uuid import uuid4

from yookassa import Configuration
from yookassa import Payment as PaymentCreator
from yookassa.domain.response import PaymentResponse

from core.settings import settings
from payments.base import BasePayment
from schemas.yookassa import Amount, Confirmation, YookassaPayment


Configuration.account_id = settings.yookassa_shop_id
Configuration.secret_key = settings.yookassa_api_key


class Yookassa(BasePayment):
    def __init__(self, amount: str, return_url: str, description: str):
        self._amount = amount
        self._return_url = return_url
        self._description = description

    def create_payment(self) -> PaymentResponse:
        payment = YookassaPayment(
            amount=Amount(value=self._amount),
            confirmation=Confirmation(return_url=self._return_url),
            description=self._description,
        )
        response = PaymentCreator.create(payment.dict(), idempotency_key=uuid4())
        return response
