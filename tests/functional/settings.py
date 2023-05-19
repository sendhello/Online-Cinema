import backoff
from pydantic import BaseSettings, Field
from dotenv import load_dotenv
from typing import Callable
load_dotenv()


class BackoffSettings(BaseSettings):
    wait_gen: Callable = backoff.expo
    raise_on_giveup: bool = False
    max_time: int = Field(60, env='CONNECTION_MAX_TIME')


class TestSettings(BaseSettings):
    redis_host: str = Field('localhost', env='REDIS_HOST')
    redis_port: int = Field('6379', env='REDIS_PORT')

    es_host: str = Field('localhost', env="ES_HOST")
    es_port: str = Field('9200', env="ES_PORT")

    es_index: str = 'movies'
    es_id_field: str = 'id'

    service_url = 'http://fastapi:8000/api/v1/'

    class Config:
        env_file = '.env'

    def get_es_hosts(self):
        return f'http://{self.es_host}:{self.es_port}'


test_settings = TestSettings()
backoff_settings = BackoffSettings()
