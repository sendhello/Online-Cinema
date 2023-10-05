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


class NotificationStatus(StrEnum):
    """Статус нотификации."""

    CREATED = auto()
    PROCESSING = auto()
    COMPLETED = auto()
    ERROR = auto()


class TaskType(StrEnum):
    """Тип таски на рассылку."""

    EMAIL = auto()
    SMS = auto()
    PUSH = auto()


class TaskStatus(StrEnum):
    """Статус таски на рассылку."""

    CREATED = auto()
    PROCESSING = auto()
    COMPLETED = auto()
    PART_COMPLETED = auto()
    ERROR = auto()
