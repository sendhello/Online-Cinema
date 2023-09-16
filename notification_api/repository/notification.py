from models import Notification

from .base import SQLAlchemyRepository


class NotificationRepository(SQLAlchemyRepository):
    sql_model = Notification
