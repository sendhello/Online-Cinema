from sqlalchemy import Boolean, Column, DateTime, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from constants import SubscribeStatus, SubscribeType
from models.payment import Payment
from .base import Base, BaseDBModel


class Subscribe(Base, BaseDBModel):
    """Модель подписок."""

    user_id = Column(UUID(as_uuid=True), nullable=False)
    subscribe_type = Column(Enum(SubscribeType))
    start_date = Column(DateTime(timezone=True))
    end_date = Column(DateTime(timezone=True))
    next_payment = Column(DateTime(timezone=True))
    auto_payment = Column(Boolean)
    status = Column(Enum(SubscribeStatus))

    payments: "list[Payment]" = relationship("Payment", back_populates="subscribe")
