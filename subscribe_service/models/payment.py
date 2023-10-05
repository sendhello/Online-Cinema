from sqlalchemy import DECIMAL, Column, DateTime, Enum, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from constants import Currency, PaymentStatus, PaymentType

from .base import Base, BaseDBModel


class Payment(Base, BaseDBModel):
    """Модель платежа."""

    payment_type = Column(Enum(PaymentType))
    payment_date = Column(DateTime(timezone=True))
    status = Column(Enum(PaymentStatus))
    user_id = Column(UUID(as_uuid=True), nullable=False)
    subscribe_id = Column(UUID(as_uuid=True), ForeignKey("subscribe.id", ondelete="SET NULL"))
    amount = Column(DECIMAL(precision=10, scale=2), nullable=False)
    currency = Column(Enum(Currency), default=Currency.RUB)
    remote_id = Column(UUID(as_uuid=True))

    subscribe = relationship("Subscribe", back_populates="payments")
