from abc import ABC
from typing import TypeVar, Sequence, Any
from uuid import UUID
from datetime import datetime
from sqlalchemy import select, and_, or_, Row, RowMapping
from sqlalchemy.ext.asyncio import AsyncSession
import logging
from models.base import Base
from schemas.base import BaseModel


logger = logging.getLogger(__name__)


SQL_MODEL = TypeVar("SQL_MODEL", bound=Base)


class SQLAlchemyRepository(ABC):
    """Abstract sqlalchemy CRUD repository"""

    sql_model = SQL_MODEL

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def create(self, obj_new: BaseModel, commit: bool = True) -> SQL_MODEL | None:
        """Commit new object to the database."""
        try:
            db_obj_new = self.sql_model(**obj_new.dict())
            self.db.add(db_obj_new)

            if commit:
                await self.db.commit()
                await self.db.refresh(db_obj_new)

                logger.info(f"Created new entity: {db_obj_new}.")

            return db_obj_new

        except Exception as e:
            await self.db.rollback()

            logger.exception("Error while uploading new object to database")
            logger.exception(e)

            raise

    async def read_by_id(
        self,
        id: UUID,
    ) -> SQL_MODEL | None:
        """Get object by id or return None."""
        res = await self.db.get(self.sql_model, id)

        return res

    async def read_optional(
        self,
        equal_fields=None,
        gt_fields=None,
        gte_fields=None,
        lt_fields=None,
        lte_fields=None,
        page: int = 1,
        page_size: int = 20,
    ) -> Sequence[SQL_MODEL] | None:
        query = select(self.sql_model)

        # Добавляем условия для сравнения
        if equal_fields:
            equal_conditions = [getattr(self.sql_model, key) == value for key, value in equal_fields.items()]
            query = query.filter(and_(*equal_conditions))

        # Добавляем условия для "больше чем"
        if gt_fields:
            gt_conditions = [getattr(self.sql_model, key) > value for key, value in gt_fields.items()]
            query = query.filter(and_(*gt_conditions))

        # Добавляем условия для "больше или равно"
        if gte_fields:
            gte_conditions = [getattr(self.sql_model, key) >= value for key, value in gte_fields.items()]
            query = query.filter(and_(*gte_conditions))

        # Добавляем условия для "меньше чем"
        if lt_fields:
            lt_conditions = [getattr(self.sql_model, key) < value for key, value in lt_fields.items()]
            query = query.filter(and_(*lt_conditions))

        # Добавляем условия для "меньше или равно"
        if lte_fields:
            lte_conditions = [getattr(self.sql_model, key) <= value for key, value in lte_fields.items()]
            query = query.filter(and_(*lte_conditions))

        query = query.order_by(self.sql_model.id).limit(page_size).offset((page - 1) * page_size)

        res = await self.db.execute(query)

        return res.scalars().all()

    async def update(self, obj_old: BaseModel, obj_new: BaseModel) -> SQL_MODEL:
        """Обновление объекта."""

        dict_new = obj_new.dict(exclude_defaults=True)
        dict_old = await self.read_by_id(obj_old.id)
        for key, value in dict_new.items():
            setattr(dict_old, key, value)

        await self.db.commit()
        await self.db.refresh(dict_old)
        return dict_old

    async def delete(
        self,
        id: UUID,
    ) -> SQL_MODEL | None:
        """Удаление объекта."""

        res = await self.db.get(self.sql_model, id)
        if res:
            await self.db.delete(res)
            await self.db.commit()
            logger.info("Entity: {res} successfully deleted from database.")
        else:
            raise ValueError(f"Entity with ID {id} not found")

        return res
