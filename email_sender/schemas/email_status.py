from uuid import UUID
from schemas.message import EmailScheme
from schemas.base import Model
from typing import Self


class EmailStatus(Model):
    """Статус отправки сообщения.

    Если ok=True - сообщение отправлено
    """

    notification_id: UUID
    ok: bool
    error: bool
    error_message: str | None
    request_id: str | None

    @classmethod
    def create(cls, email: EmailScheme, is_sent: bool, error_message: str = None) -> Self:
        status = cls(
            notification_id=email.notification_id,
            ok=is_sent,
            error=not is_sent,
            error_message=error_message,
        )
        return status
