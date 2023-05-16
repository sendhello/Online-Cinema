from pydantic import BaseSettings, Field


class TestSettings(BaseSettings):
    redis_host: str = Field('localhost', env='REDIS_HOST')
    redis_port: int = Field('6379', env='REDIS_PORT')

    es_host: str = Field('localhost', env="ES_HOST")
    es_port: str = Field('9200', env="ES_PORT")

    def get_es_hosts(self):
        return f'http://{self.es_host}:{self.es_port}'


test_settings = TestSettings()
SLEEP_TIME = 2  # seconds
