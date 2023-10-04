from logging import config as logging_config
from uuid import UUID

from pydantic import BaseSettings, Field

from core.logger import LOGGING


# Применяем настройки логирования
logging_config.dictConfig(LOGGING)


class Settings(BaseSettings):
    # Общие настройки
    project_name: str = "Subscribe Controller"
    debug: bool = Field(False, env="DEBUG")
    request_period: int = 30

    # Gateways
    subscribe_service_gateway: str
    auth_gateway: str
    notification_api_gateway: str

    admin_email: str
    admin_password: str

    subscribe_role_id: UUID


settings = Settings()
