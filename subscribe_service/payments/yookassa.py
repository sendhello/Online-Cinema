from yookassa import Configuration, Payment as PaymentCreator
from yookassa.domain.response import PaymentResponse

from core.settings import settings
from schemas.yookassa import YookassaPayment, Amount, Confirmation
from payments.base import BasePayment
from uuid import UUID, uuid4


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
