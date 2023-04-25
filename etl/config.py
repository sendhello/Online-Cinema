import logging
import os
from pathlib import Path
from pydantic import BaseSettings, Field

BASE_DIR = Path(__file__).resolve().parent


class PostgresSettings(BaseSettings):
    dbname: str = 'movies_database'
    user: str = 'app'
    password: str
    host: str = Field('127.0.0.1', env="POSTGRES_HOST")
    port: int = Field('5432', env="POSTGRES_PORT")

    class Config:
        env_file = os.path.join(BASE_DIR, '../.env')
        env_prefix = 'POSTGRES_'


class ElasticsearchSettings(BaseSettings):
    host: str = Field('localhost', env="ES_HOST")
    port: str = Field('9200', env="ES_PORT")

    class Config:
        env_file = os.path.join(BASE_DIR, '../.env')

    def get_hosts(self):
        return f'http://{self.host}:{self.port}'


postgres_settings = PostgresSettings()
elasticsearch_settings = ElasticsearchSettings()

CHUNK_SIZE = 500
TIME_INTERVAL_SECONDS = 10
