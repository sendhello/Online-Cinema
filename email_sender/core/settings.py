from logging import config as logging_config

from pydantic import BaseSettings, Field

from core.logger import LOGGING


# Применяем настройки логирования
logging_config.dictConfig(LOGGING)


class RabbitSettings(BaseSettings):
    """Настройки RabbitMQ."""

    rabbitmq_host: str
    rabbitmq_port: int
    rabbitmq_user: str
    rabbitmq_pass: str
    rabbitmq_vhost: str
    rabbitmq_exchange_type: str
    rabbitmq_prefetch_count: int
    rabbitmq_send_queue_name: str
    rabbitmq_source_queue_name: str

    @property
    def rabbitmq_dsn(self) -> str:
        return "amqp://{}:{}@{}:{}/{}".format(
            self.rabbitmq_user, self.rabbitmq_pass, self.rabbitmq_host, self.rabbitmq_port, self.rabbitmq_vhost
        )


class EmailSettings(BaseSettings):
    smtp_host: str
    smtp_port: int


class Settings(RabbitSettings, EmailSettings):
    # Общие настройки
    project_name: str = "Email Sender"
    debug: bool = False


settings = Settings()
