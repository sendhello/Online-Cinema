from datetime import datetime
from uuid import UUID

from pydantic import Field

from constants import TaskStatus, TaskType

from .base import Model


class TaskScheme(Model):
    id: UUID | None
    created_at: datetime | None
    updated_at: datetime | None
    content: str
    type: TaskType
    status: TaskStatus = Field(TaskStatus.CREATED)
    send_to: datetime
