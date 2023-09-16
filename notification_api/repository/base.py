from abc import ABC
from typing import TypeVar
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.get_logger import logger
from models.base import Base
from schemas.base import BaseModel


SQL_MODEL = TypeVar("SQL_MODEL", bound=Base)


class SQLAlchemyRepository(ABC):
    """Abstract sqlalchemy CRUD repository"""

    sql_model = SQL_MODEL

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def create(self, obj_new: BaseModel) -> BaseModel | None:
        """Commit new object to the database."""
        try:
            db_obj_new = self.sql_model(**obj_new.dict())
            self.db.add(db_obj_new)

            await self.db.commit()
            await self.db.refresh(db_obj_new)

            logger.info(f"Created new entity: {db_obj_new}.")

            return db_obj_new

        except Exception as e:
            await self.db.rollback()

            logger.exception("Error while uploading new object to database")
            logger.exception(e)

            return None

    async def read_by_id(
        self,
        id: UUID,
    ) -> sql_model | None:
        """Get object by id or return None."""
        res = await self.db.get(self.sql_model, id)

        return res

    async def read_optional(
        self,
        query: dict,
    ) -> list[sql_model] | None:
        """Get list of all objects that match with query_schema.

        If values in query schemas are not provided, they will default to None and
        will not be searched for. To search for None values specifically provide
        desired value set to None.
        """
        stmt = select(self.sql_model).filter_by(**query).order_by(self.sql_model.id)

        res = await self.db.execute(stmt)

        return res.scalars().all()

    async def update(self, obj_old: BaseModel, obj_new: BaseModel) -> sql_model:
        """Update object in db and return changed object"""
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
    ) -> sql_model | None:
        """Delete object from db by id or None if object not found in db"""
        res = await self.db.get(self.sql_model, id)
        if res:
            await self.db.delete(res)
            await self.db.commit()

            logger.info("Entitiy: {res} successfully deleted from database.")

        else:
            logger.error(f"Object with id = {id} not found in query")

        return res
