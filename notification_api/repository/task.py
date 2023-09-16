from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import joinedload

from models import Task

from .base import SQLAlchemyRepository


class TaskRepository(SQLAlchemyRepository):
    sql_model = Task

    async def read_by_id(
        self,
        id: UUID,
    ) -> sql_model | None:
        """Get object by id or return None."""
        stmt = select(self.sql_model).filter_by(id=id).options(joinedload(self.sql_model.notifications))
        res = await self.db.execute(stmt)
        return res.scalars().first()
