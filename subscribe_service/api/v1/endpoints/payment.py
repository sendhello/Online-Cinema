import logging
from datetime import datetime
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from fastapi.exceptions import HTTPException
from fastapi.responses import RedirectResponse
from starlette import status

from api.v1.deps import PaginateQueryParams
from constants import PaymentStatus, PaymentType
from schemas.payment import (
    PaymentCreateScheme,
    PaymentDBScheme,
    PaymentDBUpdateScheme,
    PaymentFindScheme,
    PaymentUpdateScheme,
)
from schemas.user import Rules, User
from security import security_jwt
from services.payment import PaymentService, get_payment_service


router = APIRouter()


@router.post("/", response_model=PaymentDBScheme)
async def create_payment(
    payment_create: PaymentCreateScheme,
    payment_service: Annotated[PaymentService, Depends(get_payment_service)],
    user: Annotated[User | None, Depends(security_jwt)],
) -> RedirectResponse | None:
    """Создание оплаты."""

    if Rules.admin_rules not in user.rules:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)

    payment = await payment_service.create(
        **payment_create.dict(),
        user_id=user.id,
    )
    payment_method = payment_service.choose_payment_method(payment)
    payment_response = payment_method.send_payment()
    await payment_service.update(
        id=payment.id,
        payment_fields=PaymentDBUpdateScheme(
            remote_id=payment_response.id,
            status=payment_response.status,
        ),
    )

    pay_url = payment_response.confirmation.confirmation_url
    logging.debug(f"Redirect to: {pay_url}")
    return RedirectResponse(url=pay_url, status_code=status.HTTP_302_FOUND)


@router.get("/{id}", response_model=PaymentDBScheme)
async def get_payment_by_id(
    id: UUID,
    payment_service: Annotated[PaymentService, Depends(get_payment_service)],
    user: Annotated[User | None, Depends(security_jwt)],
) -> PaymentDBScheme:
    """Получение платежа по его ID."""

    payment = await payment_service.get(id)
    if payment.user_id == user.id or Rules.admin_rules in user.rules:
        return payment

    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)


@router.post("/{id}/update", response_model=PaymentDBScheme)
async def update_payment_status(
    id: UUID,
    payment_service: Annotated[PaymentService, Depends(get_payment_service)],
    user: Annotated[User | None, Depends(security_jwt)],
) -> PaymentDBScheme:
    """Обновление платежа из агрегатора платежей."""

    payment = await payment_service.get(id)
    if payment.user_id != user.id and Rules.admin_rules not in user.rules:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)

    payment_method = payment_service.choose_payment_method(payment)
    payment_response = payment_method.get_payment_status()
    payment = await payment_service.update(
        id=payment.id,
        payment_fields=PaymentDBUpdateScheme(
            remote_id=payment_response.id,
            status=payment_response.status,
        ),
    )
    return payment


@router.get("/", response_model=list[PaymentDBScheme])
async def get_payments(
    paginate: Annotated[PaginateQueryParams, Depends(PaginateQueryParams)],
    payment_service: Annotated[PaymentService, Depends(get_payment_service)],
    user: Annotated[User | None, Depends(security_jwt)],
    user_id: Annotated[UUID | None, Query(description="ID пользователя")] = None,
    subscribe_id: Annotated[UUID | None, Query(description="ID подписки")] = None,
    payment_type: Annotated[PaymentType | None, Query(description="Тип подписки")] = None,
    payment_date: Annotated[datetime | None, Query(description="Дата оплаты")] = None,
    status: Annotated[PaymentStatus | None, Query(description="Статус платежа")] = None,
) -> list[PaymentDBScheme]:
    """Получение отфильтрованного списка платежей."""

    if Rules.admin_rules not in user.rules:
        user_id = user.id

    return await payment_service.find(
        PaymentFindScheme(
            user_id=user_id,
            subscribe_id=subscribe_id,
            payment_type=payment_type,
            payment_date=payment_date,
            status=status,
        ),
        page=paginate.page,
        page_size=paginate.page_size,
    )


@router.patch(
    "/{id}",
    response_model=PaymentDBScheme,
)
async def update_payment(
    id: UUID,
    payment_update: PaymentUpdateScheme,
    payment_service: Annotated[PaymentService, Depends(get_payment_service)],
    user: Annotated[User | None, Depends(security_jwt)],
) -> PaymentDBScheme | None:
    """Изменение платежа."""

    payment = await payment_service.get(id)
    if payment.user_id == user.id or Rules.admin_rules in user.rules:
        return await payment_service.update(id, payment_update)

    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)


@router.delete(
    "/{id}",
    response_model=PaymentDBScheme,
)
async def delete_payment(
    id: UUID,
    payment_service: Annotated[PaymentService, Depends(get_payment_service)],
    user: Annotated[User | None, Depends(security_jwt)],
) -> PaymentDBScheme | None:
    """Удаление платежа."""

    payment = await payment_service.get(id)
    if payment.user_id == user.id or Rules.admin_rules in user.rules:
        return await payment_service.delete(id)

    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
