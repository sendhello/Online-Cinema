from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import joinedload

from models.payment import Payment

from .base import SQLAlchemyRepository


class PaymentRepository(SQLAlchemyRepository):
    sql_model = Payment
