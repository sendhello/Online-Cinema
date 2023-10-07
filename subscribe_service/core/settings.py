import os
from logging.config import dictConfig as logger_config

from pydantic import AnyUrl, BaseSettings, HttpUrl

from core.logger import LOGGING


logger_config(LOGGING)


class PostgresSettings(BaseSettings):
    """Настройки Postgres."""

    echo_database: bool = False
    postgres_host: str
    postgres_port: int
    postgres_database: str
    postgres_user: str
    postgres_password: str

    @property
    def pg_dsn(self) -> str:
        uri = (
            f"postgresql+asyncpg://{self.postgres_user}"
            f":{self.postgres_password}@{self.postgres_host}:"
            f"{self.postgres_port}/{self.postgres_database}"
        )
        return uri


class YooKassaSettings(BaseSettings):
    """Настройки интеграции сервиса UKassa"""

    yookassa_shop_id: str
    yookassa_api_key: str
    yookassa_return_url: str


class SentrySettings(BaseSettings):
    """Настройки Sentry"""

    sentry_dsn: HttpUrl | None
    with_locals: bool = False
    shutdown_timeout: int = 30


class Settings(BaseSettings):
    project_name: str = "Subscribe Service"
    environment: str = "dev"
    debug: bool = False
    base_dir: str = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    auth_gateway: AnyUrl
    show_traceback: bool = False
    postgres: PostgresSettings = PostgresSettings()
    yookassa: YooKassaSettings = YooKassaSettings()
    sentry: SentrySettings = SentrySettings()

    @property
    def user_agent(self):
        concatenated_name = self.project_name.replace(" ", "")
        return f"{concatenated_name}/1.0"


settings = Settings()
