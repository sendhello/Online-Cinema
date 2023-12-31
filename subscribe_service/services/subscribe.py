import logging
from datetime import datetime
from functools import lru_cache
from uuid import UUID

from dateutil.relativedelta import relativedelta
from fastapi import Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from constants import ExceptionText, SubscribeStatus, SubscribeType
from db.postgres import get_session
from repository.payment import PaymentRepository
from repository.subscribe import SubscribeRepository
from schemas.subscribe import (
    SubscribeCreateScheme,
    SubscribeDBCreateScheme,
    SubscribeDBScheme,
    SubscribeFindScheme,
    SubscribeUpdateScheme,
)


logger = logging.getLogger(__name__)


class SubscribeService:
    def __init__(self, db: AsyncSession) -> None:
        self.subscribe = SubscribeRepository(db)
        self.payment = PaymentRepository(db)

    @staticmethod
    def _calculate_end_date(start_date: datetime, subscribe_type: SubscribeType):
        match subscribe_type:
            case SubscribeType.MONTHLY:
                return start_date + relativedelta(months=1)
            case SubscribeType.QUARTERLY:
                return start_date + relativedelta(months=3)
            case SubscribeType.YEARLY:
                return start_date + relativedelta(years=1)

    async def _check_exist_pending_subscribes(self, subscribe_create: SubscribeCreateScheme):
        """Проверка на существующие подписки"""

        exist_pending_subscribes = await self.find(
            subscribe_filter=SubscribeFindScheme(
                user_id=subscribe_create.user_id,
                subscribe_type=subscribe_create.subscribe_type,
                status=SubscribeStatus.PENDING,
            ),
        )
        if exist_pending_subscribes:
            subscribe_id = exist_pending_subscribes[0].id
            raise HTTPException(
                status_code=status.HTTP_423_LOCKED,
                detail=ExceptionText.user_have_pending_subscribe.format(subscribe_id=subscribe_id),
            )

    async def _get_exist_subscribes_end_date(self, subscribe_create: SubscribeCreateScheme):
        """Возвращает дату и время завершения подписки."""

        exist_active_subscribes = await self.find(
            subscribe_filter=SubscribeFindScheme(
                user_id=subscribe_create.user_id,
                status=SubscribeStatus.ACTIVE,
            ),
        )
        if exist_active_subscribes:
            return max(subscribe.end_date for subscribe in exist_active_subscribes)

    async def create(
        self,
        subscribe_data: SubscribeCreateScheme,
    ) -> SubscribeDBScheme:
        """Создание подписки."""

        await self._check_exist_pending_subscribes(subscribe_data)
        new_start_date = await self._get_exist_subscribes_end_date(subscribe_data)

        start_date = new_start_date or datetime.utcnow()
        end_date = self._calculate_end_date(start_date=start_date, subscribe_type=subscribe_data.subscribe_type)
        new_subscribe = SubscribeDBCreateScheme(
            subscribe_type=subscribe_data.subscribe_type,
            auto_payment=subscribe_data.auto_payment,
            user_id=subscribe_data.user_id,
            start_date=start_date,
            end_date=end_date,
            next_payment=end_date,
        )
        db_subscribe = await self.subscribe.create(new_subscribe)
        subscribe = SubscribeDBScheme.from_orm(db_subscribe)
        logger.debug(f"Created new subscribe: {subscribe.id}. From: {start_date}, To: {end_date}")
        return subscribe

    async def get(self, id: UUID) -> SubscribeDBScheme:
        db_subscribe = await self.subscribe.read_by_id(id)
        if not db_subscribe:
            logger.debug(f"Subscribe with {id} not found")
            raise HTTPException(detail=ExceptionText.task_not_found, status_code=status.HTTP_404_NOT_FOUND)

        return SubscribeDBScheme.from_orm(db_subscribe)

    async def find(
        self, subscribe_filter: SubscribeFindScheme, page: int = 1, page_size: int = 20
    ) -> list[SubscribeDBScheme]:
        result = await self.subscribe.read_optional(
            equal_fields=subscribe_filter.dict(
                include={"user_id", "subscribe_type", "auto_payment", "status"}, exclude_none=True
            ),
            gte_fields=subscribe_filter.dict(include={"start_date"}, exclude_none=True),
            lt_fields=subscribe_filter.dict(include={"end_date"}, exclude_none=True),
            lte_fields=subscribe_filter.dict(include={"next_payment"}, exclude_none=True),
            page=page,
            page_size=page_size,
        )
        logger.debug(f"Found subscribes: {', '.join([str(item.id) for item in result])}")
        return [SubscribeDBScheme.from_orm(item) for item in result]

    async def update(self, id: UUID, update_fields: SubscribeUpdateScheme) -> SubscribeDBScheme | None:
        old_subscribe = await self.get(id)
        db_subscribe = await self.subscribe.update(old_subscribe, update_fields)
        logger.debug("Subscribe {} was updated".format(id))
        return SubscribeDBScheme.from_orm(db_subscribe)

    async def delete(self, id: UUID) -> SubscribeDBScheme | None:
        db_subscribe = await self.subscribe.delete(id)
        if not db_subscribe:
            logger.debug("Delete failed")
            return None

        return SubscribeDBScheme.from_orm(db_subscribe)


@lru_cache
def get_subscribe_service(
    db: AsyncSession = Depends(get_session),
) -> SubscribeService:
    return SubscribeService(db)
