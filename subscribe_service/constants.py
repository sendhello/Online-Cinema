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


PRICE_MAP = {
    SubscribeType.MONTHLY: Decimal("399.00"),
    SubscribeType.QUARTERLY: Decimal("999.00"),
    SubscribeType.YEARLY: Decimal("3499.00"),
}
