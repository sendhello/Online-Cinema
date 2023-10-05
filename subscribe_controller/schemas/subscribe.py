from datetime import datetime
from uuid import UUID

from constants import SubscribeStatus, SubscribeType

from .base import Model


class SubscribeScheme(Model):
    id: UUID
    user_id: UUID
    subscribe_type: SubscribeType
    auto_payment: bool
    start_date: datetime
    end_date: datetime
    next_payment: datetime
    status: SubscribeStatus = SubscribeStatus.PENDING
