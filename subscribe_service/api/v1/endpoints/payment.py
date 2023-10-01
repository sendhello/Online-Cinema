from datetime import datetime
from typing import Annotated
from uuid import UUID
from security import security_jwt
from fastapi import APIRouter, Depends, Query
from constants import PaymentStatus, PaymentType
from schemas.payment import PaymentDBScheme, PaymentUpdateScheme, PaymentFindScheme, PaymentCreateScheme
from services.payment import PaymentService, get_payment_service
from api.v1.deps import PaginateQueryParams
from schemas.user import User


router = APIRouter()


@router.post("/", response_model=PaymentDBScheme)
async def create_payment(
    payment_create: PaymentCreateScheme,
    payment_service: Annotated[PaymentService, Depends(get_payment_service)],
    user: Annotated[User | None, Depends(security_jwt)],
) -> PaymentDBScheme | None:
    """Создание оплаты."""

    return await payment_service.create(
        **payment_create.dict(),
        user_id=user.id,
    )


@router.get("/{id}", response_model=PaymentDBScheme)
async def get_payment_by_id(
    id: UUID,
    payment_service: Annotated[PaymentService, Depends(get_payment_service)],
    user: Annotated[dict | None, Depends(security_jwt)],
) -> PaymentDBScheme:
    return await payment_service.get(id)


@router.get("/", response_model=list[PaymentDBScheme])
async def get_payments(
    paginate: Annotated[PaginateQueryParams, Depends(PaginateQueryParams)],
    payment_service: Annotated[PaymentService, Depends(get_payment_service)],
    user: Annotated[dict | None, Depends(security_jwt)],
    user_id: Annotated[UUID | None, Query(description="ID пользователя")] = None,
    subscribe_id: Annotated[UUID | None, Query(description="ID подписки")] = None,
    payment_type: Annotated[PaymentType | None, Query(description="Тип подписки")] = None,
    payment_date: Annotated[datetime | None, Query(description="Дата оплаты")] = None,
    status: Annotated[PaymentStatus | None, Query(description="Статус платежа")] = None,
) -> list[PaymentDBScheme]:
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
    payment: PaymentUpdateScheme,
    payment_service: Annotated[PaymentService, Depends(get_payment_service)],
    user: Annotated[dict | None, Depends(security_jwt)],
) -> PaymentDBScheme | None:
    return await payment_service.update(id, payment)


@router.delete(
    "/{id}",
    response_model=PaymentDBScheme,
)
async def delete_payment(
    id: UUID,
    payment_service: Annotated[PaymentService, Depends(get_payment_service)],
    user: Annotated[dict | None, Depends(security_jwt)],
) -> PaymentDBScheme | None:
    return await payment_service.delete(id)
