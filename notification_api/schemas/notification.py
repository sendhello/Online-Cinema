from datetime import datetime
from uuid import UUID

from pydantic import Field

from constants import NotificationStatus, TaskType

from .base import BaseModel


class NotificationCreateScheme(BaseModel):
    task_id: UUID
    user_id: UUID
    status: NotificationStatus = Field(NotificationStatus.CREATED)


class NotificationDBScheme(NotificationCreateScheme):
    id: UUID
    created_at: datetime
    updated_at: datetime | None

    class Config:
        orm_mode = True


class NotificationFindScheme(BaseModel):
    id: UUID | None
    created_at: datetime | None
    updated_at: datetime | None
    task_id: UUID | None
    user_id: UUID | None
    status: NotificationStatus | None


class MessageScheme(NotificationDBScheme):
    """Модель сообщения."""

    content: str
    type: TaskType
    send_to: datetime
