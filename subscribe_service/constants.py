from decimal import Decimal
from enum import Enum, auto


class StrEnum(str, Enum):
    def _generate_next_value_(name, *args) -> str:
        return name.lower()


class SubscribeType(StrEnum):
    """Тип подписки."""

    MONTHLY = auto()
    QUARTERLY = auto()
    YEARLY = auto()


class SubscribeStatus(StrEnum):
    """Статус подписки."""

    PENDING = auto()
    CANCELED = auto()
    ACTIVE = auto()
    BLOCKED = auto()


class PaymentType(StrEnum):
    """Тип платежа."""

    YOOKASSA = auto()
    SBER_PAY = auto()


class PaymentStatus(StrEnum):
    """Статус платежа."""

    CREATE = auto()
    PENDING = auto()
    WAITING_FOR_CAPTURE = auto()
    SUCCEEDED = auto()
    CANCELED = auto()
    REFUND = auto()
    ERROR = auto()


class Currency(StrEnum):
    """Валюта"""

    RUB = auto()
    USD = auto()


class ExceptionText(str, Enum):
    """Тексты ошибок."""

    error_refund = "Error refund."
    payment_not_wait_pay = "This payment not wait pay. Try create new payment"
    payment_not_succeeded = "This payment not succeeded. Action not allowed."
    invalid_auth_code = "Invalid authorization code."
    user_have_pending_subscribe = (
        ("User have pending subscribe (ID: {subscribe_id}) already. " "Please, pay this subscribe or canceled it."),
    )
    only_bearer_token = "Only Bearer token might be accepted"
    subscribe_payed = "This subscribe payed already."
    subscribe_have_pending_payment = "This subscribe have pending payment ({pending_payment}). Please try repeat pay it"
    task_not_found = "Task not found"
    payment_not_found = "Payment not found"
    payment_not_support = "Payment {payment_type} don't support now"
    not_remote_id = "Payment don't have 'remote_id'"


PRICE_MAP = {
    SubscribeType.MONTHLY: Decimal("399.00"),
    SubscribeType.QUARTERLY: Decimal("999.00"),
    SubscribeType.YEARLY: Decimal("3499.00"),
}
