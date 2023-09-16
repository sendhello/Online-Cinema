from datetime import datetime
from functools import lru_cache
from uuid import UUID

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from constants import NotificationStatus, TaskStatus
from core.get_logger import logger
from db.postgres import get_async_session
from repository.notification import NotificationRepository
from schemas.notification import MessageScheme, NotificationCreateScheme, NotificationDBScheme, NotificationFindScheme
from schemas.task import TaskFindScheme, TaskUpdateScheme
from services.task import TaskService


class NotificationService:
    def __init__(self, db: AsyncSession) -> None:
        self.notifications = NotificationRepository(db)
        self.task_service = TaskService(db)

    async def create(self, new_notification: NotificationCreateScheme) -> NotificationDBScheme | None:
        db_notification = await self.notifications.create(new_notification)
        logger.debug(f"Created new notification with ID {db_notification.id}")
        return NotificationDBScheme.from_orm(db_notification)

    async def get(self, id: UUID) -> NotificationDBScheme:
        result = await self.notifications.read_by_id(id)
        if not result:
            logger.debug("Item {} not found".format(id))
            raise RuntimeError("Notification not found")
        return NotificationDBScheme.from_orm(result)

    async def find(self, find_query: NotificationFindScheme) -> list[NotificationDBScheme]:
        result = await self.notifications.read_optional(find_query.dict(exclude_none=True))
        logger.debug("Found records")
        return [NotificationDBScheme.from_orm(item) for item in result]

    async def set_status(self, id: UUID, status: NotificationStatus, request_id: str) -> bool:
        old_notification = await self.get(id)
        await self.notifications.update(old_notification, NotificationFindScheme(status=status))
        logger.debug(f"[request_id: {request_id}] Notification with {id} set status {status.value}")

        # Устанавливаем статус таски
        task_id = old_notification.task_id
        notifications_by_task = await self.find(NotificationFindScheme(task_id=task_id))
        if all(notification.status == NotificationStatus.COMPLETED for notification in notifications_by_task):
            await self.task_service.update(task_id, TaskUpdateScheme(status=TaskStatus.COMPLETED))

        elif all(notification.status == NotificationStatus.ERROR for notification in notifications_by_task):
            await self.task_service.update(task_id, TaskUpdateScheme(status=TaskStatus.ERROR))

        elif all(
            notification.status not in [NotificationStatus.CREATED, NotificationStatus.PROCESSING]
            for notification in notifications_by_task
        ):
            await self.task_service.update(task_id, TaskUpdateScheme(status=TaskStatus.PART_COMPLETED))

        return True

    async def get_messages(self, find_query: NotificationFindScheme, need_send: bool) -> list[MessageScheme]:
        notifications = await self.find(find_query)
        task_ids = [notification.task_id for notification in notifications]
        tasks = {}
        for task_id in task_ids:
            find_tasks = await self.task_service.find(TaskFindScheme(id=task_id))
            if not find_tasks:
                raise RuntimeError(f"Task with id {task_id} not found")
            task = find_tasks[0]
            if not need_send or task.send_to < datetime.utcnow():
                tasks[task_id] = task

        filtered_notifications = [notification for notification in notifications if notification.task_id in tasks]

        return [
            MessageScheme(
                **notification.dict(),
                content=tasks[notification.task_id].content,
                type=tasks[notification.task_id].type,
                send_to=tasks[notification.task_id].send_to,
            )
            for notification in filtered_notifications
        ]


@lru_cache
def get_notification_service(
    db: AsyncSession = Depends(get_async_session),
) -> NotificationService:
    return NotificationService(db)
