from functools import lru_cache
from uuid import UUID

from fastapi import Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from core.get_logger import logger
from db.postgres import get_async_session
from models import Task
from repository.notification import NotificationRepository
from repository.task import TaskRepository
from schemas.notification import NotificationCreateScheme
from schemas.task import (
    TaskCreateDbScheme,
    TaskCreateScheme,
    TaskFindScheme,
    TaskUpdateScheme,
)


class TaskService:
    def __init__(self, db: AsyncSession) -> None:
        self.tasks = TaskRepository(db)
        self.notifications = NotificationRepository(db)

    async def create(self, new_task: TaskCreateScheme) -> Task | None:
        """Создание таски."""

        user_ids = new_task.user_ids
        task = TaskCreateDbScheme.parse_obj(new_task)
        db_task = await self.tasks.create(task)
        logger.debug(f"Created new task: {db_task.id}")

        for user_id in user_ids:
            notification = NotificationCreateScheme(
                task_id=db_task.id,
                user_id=user_id,
            )
            db_notification = await self.notifications.create(notification)
            logger.debug(f"Created new notification with ID {db_notification.id}")

        return db_task

    async def get(self, id: UUID) -> Task:
        db_task = await self.tasks.read_by_id(id)
        if not db_task:
            logger.debug(f"Task with {id} not found")
            raise HTTPException(status_code=404, detail="Task not found")

        return db_task

    async def find(self, find_query: TaskFindScheme) -> list[Task]:
        result = await self.tasks.read_optional(find_query.dict(exclude_none=True))
        logger.debug(f"Found records: {', '.join([str(item.id) for item in result])}")
        return result

    async def update(self, id: UUID, task: TaskUpdateScheme) -> Task | None:
        old_item = await self.get(id)
        result = await self.tasks.update(old_item, task)
        logger.debug("Item {} was updated".format(id))
        return result

    async def delete(self, id: UUID) -> Task | None:
        result = await self.tasks.delete(id)
        if not result:
            logger.debug("Delete failed")
            return None

        return result


@lru_cache
def get_task_service(
    db: AsyncSession = Depends(get_async_session),
) -> TaskService:
    return TaskService(db)
