from datetime import datetime
from uuid import UUID

from pydantic import Field

from constants import TaskStatus, TaskType
from schemas.notification import NotificationDBScheme

from .base import BaseModel


class TaskCreateScheme(BaseModel):
    content: str
    type: TaskType
    user_ids: list[UUID]
    send_to: datetime


class TaskCreateDbScheme(BaseModel):
    content: str
    type: TaskType
    status: TaskStatus = Field(TaskStatus.CREATED)
    send_to: datetime


class TaskDbScheme(BaseModel):
    id: UUID | None
    created_at: datetime | None
    updated_at: datetime | None
    content: str
    type: TaskType
    status: TaskStatus = Field(TaskStatus.CREATED)
    send_to: datetime

    class Config:
        orm_mode = True


class TaskFullDbScheme(BaseModel):
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


class TaskUpdateScheme(BaseModel):
    content: str | None
    type: TaskType | None
    send_to: datetime | None
    status: TaskStatus | None


class TaskFindScheme(BaseModel):
    id: UUID | None
    created_at: datetime | None
    updated_at: datetime | None
    type: TaskType | None
    status: TaskStatus | None
    send_to: datetime | None
