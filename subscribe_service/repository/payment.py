from models.payment import Payment

from .base import SQLAlchemyRepository


class PaymentRepository(SQLAlchemyRepository):
    sql_model = Payment
