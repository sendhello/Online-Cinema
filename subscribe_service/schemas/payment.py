from datetime import date, datetime
from decimal import Decimal
from uuid import UUID

from constants import Currency, PaymentStatus, PaymentType

from .base import Model


class PaymentCreateScheme(Model):
    subscribe_id: UUID
    payment_type: PaymentType


class PaymentDBCreateScheme(Model):
    user_id: UUID
    subscribe_id: UUID
    payment_type: PaymentType
    payment_date: datetime
    status: PaymentStatus = PaymentStatus.CREATE
    currency: Currency = Currency.RUB
    amount: Decimal


class PaymentDBScheme(PaymentDBCreateScheme):
    id: UUID
    subscribe_id: UUID | None
    remote_id: UUID | None

    class Config:
        orm_mode = True


class PaymentUpdateScheme(Model):
    status: PaymentStatus | None
    subscribe_id: UUID | None


class PaymentDBUpdateScheme(PaymentUpdateScheme):
    remote_id: UUID | None


class PaymentFindScheme(Model):
    user_id: UUID | None
    remote_id: UUID | None
    subscribe_id: UUID | None
    payment_type: PaymentType | None
    payment_date: date | None
    status: PaymentStatus | None
    currency: Currency | None
    amount: Decimal | None
