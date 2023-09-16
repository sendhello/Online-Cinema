from datetime import datetime
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query

from constants import TaskStatus, TaskType
from schemas.task import TaskCreateScheme, TaskDbScheme, TaskFindScheme, TaskFullDbScheme, TaskUpdateScheme
from services.task import TaskService, get_task_service


router = APIRouter(tags=["Tasks"])


@router.post(
    "/",
)
async def create_task(
    task: TaskCreateScheme,
    task_service: TaskService = Depends(get_task_service),
) -> TaskDbScheme | None:
    """Создание таски."""

    return await task_service.create(task)


@router.get("/{id}", response_model=TaskFullDbScheme)
async def get_task_by_id(
    id: UUID,
    task_service: TaskService = Depends(get_task_service),
) -> TaskFullDbScheme:
    return await task_service.get(id)


@router.get("/", response_model=list[TaskDbScheme])
async def get_tasks(
    id: Annotated[UUID | None, Query(title="ID задачи")] = None,
    created_at: Annotated[datetime | None, Query(title="Дата создания")] = None,
    updated_at: Annotated[datetime | None, Query(title="Дата обновления")] = None,
    type: Annotated[TaskType | None, Query(title="Тип задачи")] = None,
    status: Annotated[TaskStatus | None, Query(title="Статус задачи")] = None,
    send_to: Annotated[
        datetime | None,
        Query(title="Дата и время запланированной отправки"),
    ] = None,
    task_service: TaskService = Depends(get_task_service),
) -> list[TaskDbScheme]:
    return await task_service.find(
        TaskFindScheme(
            id=id,
            created_at=created_at,
            updated_at=updated_at,
            type=type,
            status=status,
            send_to=send_to,
        )
    )


@router.patch(
    "/{id}",
)
async def update__task(
    id: UUID,
    task: TaskUpdateScheme,
    task_service: TaskService = Depends(get_task_service),
) -> TaskDbScheme | None:
    return await task_service.update(id, task)


@router.delete(
    "/{id}",
)
async def delete_task(
    id: UUID,
    task_service: TaskService = Depends(get_task_service),
) -> TaskDbScheme | None:
    return await task_service.delete(id)
