from datetime import datetime
from uuid import UUID

from pydantic import Field

from constants import TaskStatus, TaskType
from schemas.notification import NotificationDBScheme

from .base import Model


class TaskCreateScheme(Model):
    content: str
    type: TaskType
    user_ids: list[UUID]
    send_to: datetime


class TaskCreateDbScheme(Model):
    content: str
    type: TaskType
    status: TaskStatus = Field(TaskStatus.CREATED)
    send_to: datetime


class TaskDbScheme(Model):
    id: UUID | None
    created_at: datetime | None
    updated_at: datetime | None
    content: str
    type: TaskType
    status: TaskStatus = Field(TaskStatus.CREATED)
    send_to: datetime

    class Config:
        orm_mode = True


class TaskFullDbScheme(Model):
    id: UUID | None
    created_at: datetime | None
    updated_at: datetime | None
    content: str
    type: TaskType
    status: TaskStatus = Field(TaskStatus.CREATED)
    send_to: datetime
    notifications: list[NotificationDBScheme]

    class Config:
        orm_mode = True


class TaskUpdateScheme(Model):
    content: str | None
    type: TaskType | None
    send_to: datetime | None
    status: TaskStatus | None


class TaskFindScheme(Model):
    id: UUID | None
    created_at: datetime | None
    updated_at: datetime | None
    type: TaskType | None
    status: TaskStatus | None
    send_to: datetime | None
