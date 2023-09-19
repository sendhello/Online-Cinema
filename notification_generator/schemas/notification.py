from datetime import datetime
from uuid import UUID

from pydantic import Field

from constants import NotificationStatus, TaskType

from .base import Model


class NotificationScheme(Model):
    """Модель сообщения."""

    id: UUID
    task_id: UUID
    user_id: UUID
    status: NotificationStatus = Field(NotificationStatus.CREATED)
    created_at: datetime
    updated_at: datetime | None
    content: str
    type: TaskType
    send_to: datetime
