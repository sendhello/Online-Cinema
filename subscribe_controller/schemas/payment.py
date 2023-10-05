from datetime import datetime
from decimal import Decimal
from uuid import UUID

from constants import Currency, PaymentStatus, PaymentType

from .base import Model


class PaymentScheme(Model):
    """Модель оплаты"""

    id: UUID
    user_id: UUID
    subscribe_id: UUID
    payment_type: PaymentType
    payment_date: datetime
    status: PaymentStatus = PaymentStatus.CREATE
    currency: Currency = Currency.RUB
    amount: Decimal
    subscribe_id: UUID | None
    remote_id: UUID | None
