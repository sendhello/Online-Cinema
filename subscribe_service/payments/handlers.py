from logging import getLogger

from fastapi.exceptions import HTTPException
from starlette import status

from constants import PaymentType
from core.settings import settings
from payments.yookassa import PaymentResponse, Yookassa
from schemas.payment import PaymentDBScheme


logger = getLogger(__name__)


def chose_payment(payment_type: PaymentType) -> type:
    """Выбор платежного шлюза."""

    match payment_type:
        case PaymentType.YOOKASSA:
            payment_class = Yookassa

        case PaymentType.SBER_PAY:
            raise HTTPException(status.HTTP_423_LOCKED, "SberPay don't support now")

        case _:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, f"Payment {payment_type} don't support now")

    return payment_class


def send_payment(payment: PaymentDBScheme) -> PaymentResponse:
    """Отправка платежа."""

    payment_class = chose_payment(payment.payment_type)
    payment: Yookassa = payment_class(
        amount=payment.amount,
        return_url=settings.yookassa_return_url,
        description=f"payment_id={payment.id}",
    )
    response = payment.create_payment()
    logger.info(f"Yookassa payment response: {response.json()}")
    return response
