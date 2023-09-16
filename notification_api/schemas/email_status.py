from uuid import UUID

from schemas.base import Model


class EmailStatus(Model):
    """Статус отправки сообщения.

    Если ok=True - сообщение отправлено
    """

    notification_id: UUID
    ok: bool
    error: bool
    error_message: str | None
    request_id: str | None
