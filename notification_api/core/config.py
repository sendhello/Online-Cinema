import os

from pydantic import AnyUrl, BaseSettings


class ProjectSettings(BaseSettings):
    # Название проекта. Используется в Swagger-документации
    project_name: str = "Notification API"
    # Корень проекта
    base_dir: str = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    backoff_max_time: int = 60

    auth_gateway: AnyUrl
    show_traceback: bool = False

    @property
    def user_agent(self):
        concatenated_name = self.project_name.replace(" ", "")
        return f"{concatenated_name}/1.0"


class PostgresSettings(BaseSettings):
    """Настройки Postgres."""

    echo_database: bool = False
    postgres_host: str
    postgres_port: int
    postgres_database: str
    postgres_user: str
    postgres_password: str

    @property
    def pg_uri(self) -> str:
        return (
            f"postgresql+asyncpg://{self.postgres_user}"
            f":{self.postgres_password}@{self.postgres_host}:"
            f"{self.postgres_port}/{self.postgres_database}"
        )


class RabbitSettings(BaseSettings):
    """Настройки RabbitMQ."""

    rabbitmq_host: str
    rabbitmq_port: int
    rabbitmq_user: str
    rabbitmq_pass: str
    rabbitmq_vhost: str
    rabbitmq_exchange_type: str
    rabbitmq_prefetch_count: int
    rabbitmq_source_queue_name: str

    @property
    def rabbitmq_dsn(self) -> str:
        return "amqp://{}:{}@{}:{}/{}".format(
            self.rabbitmq_user, self.rabbitmq_pass, self.rabbitmq_host, self.rabbitmq_port, self.rabbitmq_vhost
        )


project_settings = ProjectSettings()
postgres_settings = PostgresSettings()
rabbit_settings = RabbitSettings()
