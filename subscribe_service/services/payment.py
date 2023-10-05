import logging
from datetime import datetime
from functools import lru_cache
from uuid import UUID

from fastapi import Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from constants import PRICE_MAP, PaymentStatus, PaymentType, SubscribeType
from db.postgres import get_session
from repository.payment import PaymentRepository
from schemas.payment import PaymentDBCreateScheme, PaymentDBScheme, PaymentFindScheme, PaymentUpdateScheme
from services.yookassa import YookassaService


logger = logging.getLogger(__name__)


class PaymentService:
    def __init__(self, db: AsyncSession) -> None:
        self.payment = PaymentRepository(db)

    async def _check_exist_payments(self, subscribe_id: UUID, payment_type: PaymentType):
        """Проверка существующих оплат"""

        exist_payments = await self.find(
            PaymentFindScheme(
                subscribe_id=subscribe_id,
                payment_type=payment_type,
            ),
        )
        if any(payment.status == PaymentStatus.SUCCEEDED for payment in exist_payments):
            raise HTTPException(status_code=status.HTTP_423_LOCKED, detail="This subscribe payed already.")

        pending_payments = [payment for payment in exist_payments if payment.status == PaymentStatus.PENDING]
        if pending_payments:
            pending_payment = pending_payments[0].id
            raise HTTPException(
                status_code=status.HTTP_423_LOCKED,
                detail=f"This subscribe have pending payment ({pending_payment}). Please try repeat pay it",
            )

    async def create(
        self, subscribe_id: UUID, subscribe_type: SubscribeType, user_id: UUID, payment_type: PaymentType
    ) -> PaymentDBScheme:
        """Создание оплаты."""

        await self._check_exist_payments(subscribe_id, payment_type)

        amount = PRICE_MAP[subscribe_type]
        new_payment = PaymentDBCreateScheme(
            user_id=user_id,
            subscribe_id=subscribe_id,
            payment_type=payment_type,
            payment_date=datetime.utcnow(),
            amount=amount,
        )
        db_payment = await self.payment.create(new_payment)
        payment = PaymentDBScheme.from_orm(db_payment)
        logger.debug(f"Created new payment: {payment.id}")
        return payment

    async def get(self, id: UUID) -> PaymentDBScheme:
        db_payment = await self.payment.read_by_id(id)
        if not db_payment:
            logger.debug(f"Payment with {id} not found")
            raise ValueError("Payment not found")

        return PaymentDBScheme.from_orm(db_payment)

    async def find(
        self, payment_filter: PaymentFindScheme, page: int = 1, page_size: int = 20
    ) -> list[PaymentDBScheme]:
        db_payments = await self.payment.read_optional(
            equal_fields=payment_filter.dict(
                include={"user_id", "subscribe_id", "payment_type", "status", "currency", "amount", "remote_id"},
                exclude_none=True,
            ),
            gte_fields={"payment_date": datetime.combine(payment_filter.payment_date, datetime.min.time())}
            if payment_filter.payment_date is not None
            else None,
            lt_fields={"payment_date": datetime.combine(payment_filter.payment_date, datetime.max.time())}
            if payment_filter.payment_date is not None
            else None,
            page=page,
            page_size=page_size,
        )
        logger.debug(f"Found payments: {', '.join([str(db_payment.id) for db_payment in db_payments])}")
        return [PaymentDBScheme.from_orm(db_payment) for db_payment in db_payments]

    async def update(self, id: UUID, payment_fields: PaymentUpdateScheme) -> PaymentDBScheme | None:
        old_payment = await self.get(id)
        db_payment = await self.payment.update(old_payment, payment_fields)
        logger.debug("Payment {} was updated".format(id))
        return PaymentDBScheme.from_orm(db_payment)

    async def delete(self, id: UUID) -> PaymentDBScheme | None:
        db_payment = await self.payment.delete(id)
        if not db_payment:
            logger.debug("Delete failed")
            return None

        return PaymentDBScheme.from_orm(db_payment)

    @staticmethod
    def choose_payment_method(payment: PaymentDBScheme) -> YookassaService:
        """Выбор метода оплаты."""

        match payment.payment_type:
            case PaymentType.YOOKASSA:
                return YookassaService(payment)

            case PaymentType.SBER_PAY:
                raise RuntimeError(f"Payment {payment.payment_type}  don't support now")

            case _:
                raise RuntimeError(f"Payment {payment.payment_type} don't support now")


@lru_cache
def get_payment_service(
    db: AsyncSession = Depends(get_session),
) -> PaymentService:
    return PaymentService(db)
