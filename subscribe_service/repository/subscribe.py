from models.subscribe import Subscribe

from .base import SQLAlchemyRepository


class SubscribeRepository(SQLAlchemyRepository):
    sql_model = Subscribe
