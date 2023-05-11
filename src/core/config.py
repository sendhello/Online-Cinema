import os
from logging import config as logging_config

from pydantic import BaseSettings, Field

from core.logger import LOGGING

# Применяем настройки логирования
logging_config.dictConfig(LOGGING)


class Settings(BaseSettings):
    # Название проекта. Используется в Swagger-документации
    project_name: str = Field('movies', env='PROJECT_NAME')

    # Настройки Redis
    redis_host: str = Field('127.0.0.1', env='REDIS_HOST')
    redis_port: int = Field(6377, env='REDIS_PORT')

    # Настройки Elasticsearch
    elastic_host: str = Field('127.0.0.1', env='ES_HOST')
    elastic_port: int = Field(9200, env='ES_PORT')

    # Корень проекта
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


settings = Settings()
