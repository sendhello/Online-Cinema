from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import joinedload

from models.subscribe import Subscribe

from .base import SQLAlchemyRepository


class SubscribeRepository(SQLAlchemyRepository):
    sql_model = Subscribe