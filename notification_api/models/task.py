from sqlalchemy import Column, DateTime, Enum, MetaData, Text
from sqlalchemy.orm import relationship

from constants import TaskStatus, TaskType

from .base import Base, BaseDBModel


class Task(Base, BaseDBModel):
    """Database models representing 'task' table in db.

    'id' and 'tablename' are created automatically by 'BaseDBModel'.
    """

    __metadata__ = MetaData()

    content = Column(Text())
    type = Column(Enum(TaskType))
    status = Column(Enum(TaskStatus))
    send_to = Column(DateTime(timezone=True))
    notifications = relationship("Notification", back_populates="task", passive_deletes=True)
