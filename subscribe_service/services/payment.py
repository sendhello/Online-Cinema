from functools import lru_cache
from uuid import UUID
from datetime import datetime
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from schemas.subscribe import SubscribeDBScheme
import logging
from constants import SubscribeType, PRICE_MAP
from typing import Sequence
from db.postgres import get_session
from models.payment import Payment
from repository.payment import PaymentRepository
from schemas.payment import (
    PaymentDBScheme,
    PaymentFindScheme,
    PaymentCreateScheme,
    PaymentDBCreateScheme,
    PaymentUpdateScheme,
)
from constants import PaymentType, PaymentStatus


logger = logging.getLogger(__name__)


class PaymentService:
    def __init__(self, db: AsyncSession) -> None:
        self.payment = PaymentRepository(db)

    async def create(
        self, subscribe_id: UUID, subscribe_type: SubscribeType, user_id: UUID, payment_type: PaymentType
    ) -> PaymentDBScheme:
        """Создание оплаты."""

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

    async def find(self, payment_filter: PaymentFindScheme, page: int, page_size: int) -> list[PaymentDBScheme]:
        db_payments = await self.payment.read_optional(
            equal_fields=payment_filter.dict(
                include={'user_id', 'subscribe_id', 'payment_type', 'status', 'currency', 'amount'}, exclude_none=True
            ),
            gte_fields={'payment_date': datetime.combine(payment_filter.payment_date, datetime.min.time())}
            if payment_filter.payment_date is not None
            else None,
            lt_fields={'payment_date': datetime.combine(payment_filter.payment_date, datetime.max.time())}
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


@lru_cache
def get_payment_service(
    db: AsyncSession = Depends(get_session),
) -> PaymentService:
    return PaymentService(db)
