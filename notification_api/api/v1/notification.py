from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query

from constants import NotificationStatus
from schemas.notification import (
    MessageScheme,
    NotificationDBScheme,
    NotificationFindScheme,
)
from services.notification import NotificationService, get_notification_service


router = APIRouter(tags=["Notification"])


@router.get("/{id}", response_model=NotificationDBScheme)
async def get_notification_tasks(
    id: UUID,
    notification_service: NotificationService = Depends(get_notification_service),
) -> NotificationDBScheme:
    return await notification_service.get(id)


@router.get("/", response_model=list[MessageScheme])
async def find_notification_tasks(
    id: Annotated[UUID | None, Query(title="ID сообщения")] = None,
    task_id: Annotated[UUID | None, Query(title="ID задачи")] = None,
    user_id: Annotated[UUID | None, Query(title="ID пользователя")] = None,
    status: Annotated[NotificationStatus | None, Query(title="Статус сообщения")] = None,
    need_send: Annotated[bool, Query(title="Флаг: к отправке сейчас")] = False,
    notification_service: NotificationService = Depends(get_notification_service),
) -> list[NotificationDBScheme]:
    messages = await notification_service.get_messages(
        NotificationFindScheme(
            id=id,
            task_id=task_id,
            user_id=user_id,
            status=status,
        ),
        need_send=need_send,
    )
    return messages
