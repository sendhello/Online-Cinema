from datetime import timedelta
from logging import config as logging_config

from async_fastapi_jwt_auth import AuthJWT
from core.logger import LOGGING
from pydantic import BaseSettings, Field, PostgresDsn


# Применяем настройки логирования
logging_config.dictConfig(LOGGING)


class Settings(BaseSettings):
    # Общие настройки
    project_name: str = Field('Auth', env='PROJECT_NAME')
    debug: bool = Field(False, env='DEBUG')

    # Настройки Redis
    redis_host: str = Field('127.0.0.1', env='REDIS_HOST')
    redis_port: int = Field(6379, env='REDIS_PORT')

    # Настройки Postgres
    pg_dsn: PostgresDsn = Field(
        'postgresql+asyncpg://app:123qwe@localhost:5433/auth', env='PG_DSN'
    )

    # Настройки AuthJWT
    authjwt_secret_key: str = Field('secret', env='SECRET_KEY')
    authjwt_access_token_expires: timedelta = timedelta(minutes=15)
    authjwt_refresh_token_expires: timedelta = timedelta(days=30)

    # Настройка телеметрии
    jaeger_trace: bool = Field(True, env='JAEGER_TRACE')
    jaeger_agent_host: str = Field('localhost', env='JAEGER_AGENT_HOST')
    jaeger_agent_port: int = Field(6831, env='JAEGER_AGENT_PORT')

    # Настройки лимитирования запросов
    request_limit: int = Field(20, env='REQUEST_LIMIT_PER_MINUTE')


@AuthJWT.load_config
def get_config():
    return Settings()


settings = Settings()
