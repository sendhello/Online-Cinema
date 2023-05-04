from pathlib import Path

from pydantic import BaseSettings, Field

BASE_DIR = Path(__file__).resolve().parent.parent


class PostgresSettings(BaseSettings):
    dbname: str = Field('postgres', env="DB_NAME")
    user: str = Field('postgres', env="DB_USER")
    password: str = Field('postgres', env="DB_PASSWORD")
    host: str = Field('127.0.0.1', env="DB_HOST")
    port: int = Field('5432', env="DB_PORT")


class ElasticsearchSettings(BaseSettings):
    host: str = Field('localhost', env="ES_HOST")
    port: str = Field('9200', env="ES_PORT")

    def get_hosts(self):
        return f'http://{self.host}:{self.port}'


class RedisSettings(BaseSettings):
    host: str = Field('localhost', env='REDIS_HOST')
    port: int = Field('6379', env='REDIS_PORT')


postgres_settings = PostgresSettings()
elasticsearch_settings = ElasticsearchSettings()
redis_settings = RedisSettings()

CHUNK_SIZE = 500
TIME_INTERVAL_SECONDS = 10
