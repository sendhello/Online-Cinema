import os
from logging import config as logging_config

from core.logger import LOGGING
from pydantic import BaseSettings, Field, PostgresDsn

# Применяем настройки логирования
logging_config.dictConfig(LOGGING)


class Settings(BaseSettings):
    # Название проекта. Используется в Swagger-документации
    project_name: str = Field("Auth", env="PROJECT_NAME")

    # Настройки Redis
    redis_host: str = Field("127.0.0.1", env="REDIS_HOST")
    redis_port: int = Field(6377, env="REDIS_PORT")

    # Настройки Postgres
    pg_dsn: PostgresDsn = Field(
        "postgresql+asyncpg://app:qwe123@localhost:5433/auth", env="PG_DSN"
    )


settings = Settings()
