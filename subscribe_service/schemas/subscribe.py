from datetime import date, datetime
from uuid import UUID

from pydantic import validator

from constants import PaymentType, SubscribeStatus, SubscribeType

from .base import Model


class SubscribeCreateScheme(Model):
    user_id: UUID | None
    subscribe_type: SubscribeType
    payment_type: PaymentType
    auto_payment: bool = True


class SubscribeDBCreateScheme(Model):
    user_id: UUID
    subscribe_type: SubscribeType
    auto_payment: bool
    start_date: datetime
    end_date: datetime
    next_payment: datetime
    status: SubscribeStatus = SubscribeStatus.PENDING


class SubscribeDBScheme(SubscribeDBCreateScheme):
    id: UUID

    class Config:
        orm_mode = True


class SubscribeUpdateScheme(Model):
    user_id: UUID | None
    subscribe_type: SubscribeType | None
    start_date: datetime | None
    end_date: datetime | None
    next_payment: datetime | None
    auto_payment: bool | None
    status: SubscribeStatus | None


class SubscribeFindScheme(Model):
    user_id: UUID | None
    subscribe_type: SubscribeType | None
    start_date: datetime | date | None
    end_date: datetime | date | None
    next_payment: datetime | date | None
    auto_payment: bool | None
    status: SubscribeStatus | None

    @validator("next_payment")
    def convert_date_to_up(cls, v):
        if isinstance(v, date):
            return datetime.combine(v, datetime.max.time())

        return v

    @validator("start_date", "end_date")
    def convert_date_to_down(cls, v):
        if isinstance(v, date):
            return datetime.combine(v, datetime.min.time())

        return v
