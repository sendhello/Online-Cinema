import os
from logging import config as logging_config

from pydantic import BaseSettings, Field, PostgresDsn

from core.logger import LOGGING

# Применяем настройки логирования
logging_config.dictConfig(LOGGING)


class AppSettings(BaseSettings):
    # Название проекта. Используется в Swagger-документации
    project_name: str = Field('Auth', env='PROJECT_NAME')

    # Настройки Redis
    redis_host: str = Field('127.0.0.1', env='REDIS_HOST')
    redis_port: int = Field(6377, env='REDIS_PORT')

    # Настройки Postgres
    PG_DSN: PostgresDsn = Field('postgres://user:pass@localhost:5432/foobar', env='PG_DSN')


app_settings = AppSettings()
