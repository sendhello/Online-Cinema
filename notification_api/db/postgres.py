from typing import AsyncGenerator

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from core.config import postgres_settings
from core.get_logger import logger


# Создаём движок
# Настройки подключения к БД передаём из переменных окружения, которые заранее загружены в файл настроек
engine = create_async_engine(postgres_settings.pg_uri, echo=postgres_settings.echo_database, future=True)
async_session = async_sessionmaker(engine, expire_on_commit=False)


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    """Yield an async session.

    All conversations with the database are established via the session
    objects. Also. the sessions act as holding zone for ORM-mapped objects.
    """
    async with async_session() as async_sess:
        try:
            yield async_sess

        except SQLAlchemyError as e:
            logger.error("Unable to yield session in database dependency")
            logger.error(e)
