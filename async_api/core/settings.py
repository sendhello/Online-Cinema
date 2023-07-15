import os
from logging import config as logging_config

from core.logger import LOGGING
from pydantic import BaseSettings, Field


# Применяем настройки логирования
logging_config.dictConfig(LOGGING)


class Settings(BaseSettings):
    # Общие настройки
    project_name: str = Field('movies', env='PROJECT_NAME')
    debug: bool = Field(False, env='DEBUG')

    # Настройки Redis
    redis_host: str = Field('127.0.0.1', env='REDIS_HOST')
    redis_port: int = Field(6377, env='REDIS_PORT')

    # Настройки Elasticsearch
    elastic_host: str = Field('127.0.0.1', env='ES_HOST')
    elastic_port: int = Field(9200, env='ES_PORT')

    # Корень проекта
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    # Настройки авторизации
    jwt_secret_key: str = Field('secret', env='SECRET_KEY')
    jwt_algorithm: str = Field('HS256', env='JWT_ALGORITHM')

    # Настройка телеметрии
    jaeger_trace: bool = Field(True, env='JAEGER_TRACE')
    jaeger_agent_host: str = Field('localhost', env='JAEGER_AGENT_HOST')
    jaeger_agent_port: int = Field(6831, env='JAEGER_AGENT_PORT')


settings = Settings()
