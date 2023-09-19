from uuid import UUID

from pydantic import EmailStr, Field

from .base import Model


class EmailScheme(Model):
    """Модель email-сообщения."""

    notification_id: UUID = Field(description="ID уведомления")
    email: EmailStr = Field("Уведомление", description="Тема письма")
    subject: str = Field("Уведомление", description="Тема письма")
    from_email: EmailStr = Field("no-reply@example.com", description="Email-адрес отправителя")
    from_name: str = Field("Онлайн-Кинотеатр", description="Имя отправителя")
    body: str = Field(description="Тело письма")
