import logging
from datetime import date, datetime
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from fastapi.responses import RedirectResponse
from fastapi.exceptions import HTTPException

from api.v1.deps import PaginateQueryParams
from constants import SubscribeType
from payments.handlers import send_payment
from schemas.payment import PaymentDBUpdateScheme
from schemas.subscribe import SubscribeCreateScheme, SubscribeDBScheme, SubscribeFindScheme, SubscribeUpdateScheme
from schemas.user import User
from security import security_jwt
from schemas.user import Rules
from services.payment import PaymentService, get_payment_service
from services.subscribe import SubscribeService, get_subscribe_service
from starlette import status


router = APIRouter()


@router.post("/")
async def create_subscribe(
    subscribe_create: SubscribeCreateScheme,
    subscribe_service: Annotated[SubscribeService, Depends(get_subscribe_service)],
    payment_service: Annotated[PaymentService, Depends(get_payment_service)],
    user: Annotated[User | None, Depends(security_jwt)],
) -> RedirectResponse:
    """Создание подписки."""

    if Rules.admin_rules not in user.rules:
        subscribe_create.user_id = user.id

    subscribe = await subscribe_service.create(subscribe_create)
    payment = await payment_service.create(
        subscribe_id=subscribe.id,
        subscribe_type=subscribe.subscribe_type,
        user_id=subscribe_create.user_id,
        payment_type=subscribe_create.payment_type,
    )
    payment_response = send_payment(payment=payment)
    await payment_service.update(
        id=payment.id,
        payment_fields=PaymentDBUpdateScheme(
            remote_id=payment_response.id,
            status=payment_response.status,
        ),
    )

    pay_url = payment_response.confirmation.confirmation_url
    logging.debug(f"Redirect to: {pay_url}")
    return RedirectResponse(url=pay_url)


@router.get("/{id}", response_model=SubscribeDBScheme)
async def get_subscribe_by_id(
    id: UUID,
    subscribe_service: Annotated[SubscribeService, Depends(get_subscribe_service)],
    user: Annotated[User | None, Depends(security_jwt)],
) -> SubscribeDBScheme | None:
    """Получение подписки по ее ID."""

    subscribe = await subscribe_service.get(id)
    if subscribe.user_id == user.id or Rules.admin_rules in user.rules:
        return subscribe

    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)

@router.get("/", response_model=list[SubscribeDBScheme])
async def get_subscribes(
    paginate: Annotated[PaginateQueryParams, Depends(PaginateQueryParams)],
    subscribe_service: Annotated[SubscribeService, Depends(get_subscribe_service)],
    user: Annotated[User | None, Depends(security_jwt)],
    user_id: Annotated[UUID | None, Query(description="ID пользователя")] = None,
    type: Annotated[SubscribeType | None, Query(description="Тип подписки")] = None,
    start_date: Annotated[datetime | date | None, Query(description="Дата начала подписки")] = None,
    end_date: Annotated[datetime | date | None, Query(description="Дата окончания подписки")] = None,
    next_payment: Annotated[date | None, Query(description="Дата следующего платежа")] = None,
    auto_payment: Annotated[bool | None, Query(description="Автоплатеж")] = None,
    is_active: Annotated[bool | None, Query(description="Подписка активна")] = None,
) -> list[SubscribeDBScheme]:
    """Получение отфильтрованного списка подписок."""

    if Rules.admin_rules not in user.rules:
        user_id = user.id

    res = await subscribe_service.find(
        subscribe_filter=SubscribeFindScheme(
            user_id=user_id,
            subscribe_type=type,
            start_date=start_date,
            end_date=end_date,
            next_payment=next_payment,
            auto_payment=auto_payment,
            is_active=is_active,
        ),
        page=paginate.page,
        page_size=paginate.page_size,
    )
    return res


@router.patch(
    "/{id}",
    response_model=SubscribeDBScheme,
)
async def update_subscribe(
    id: UUID,
    subscribe_update: SubscribeUpdateScheme,
    subscribe_service: Annotated[SubscribeService, Depends(get_subscribe_service)],
    user: Annotated[User | None, Depends(security_jwt)],
) -> SubscribeDBScheme | None:
    """Изменение подписки."""

    subscribe = await subscribe_service.get(id)
    if subscribe.user_id == user.id or Rules.admin_rules in user.rules:
        return await subscribe_service.update(id, subscribe_update)

    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)


@router.delete(
    "/{id}",
    response_model=SubscribeDBScheme,
)
async def delete_subscribe(
    id: UUID,
    subscribe_service: Annotated[SubscribeService, Depends(get_subscribe_service)],
    user: Annotated[User | None, Depends(security_jwt)],
) -> SubscribeDBScheme | None:
    """Удаление подписки."""

    subscribe = await subscribe_service.get(id)
    if subscribe.user_id == user.id or Rules.admin_rules in user.rules:
        return await subscribe_service.delete(id)

    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
