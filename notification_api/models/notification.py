from sqlalchemy import Column, Enum, ForeignKey, MetaData
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from constants import NotificationStatus

from .base import Base, BaseDBModel


class Notification(Base, BaseDBModel):
    """Database models representing 'notification' table in db.

    'id' and 'tablename' are created automatically by 'BaseDBModel'.
    """

    __metadata__ = MetaData()

    task_id = Column(UUID, ForeignKey("task.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(UUID, nullable=False)
    status = Column(Enum(NotificationStatus))
    task = relationship("Task", back_populates="notifications")
