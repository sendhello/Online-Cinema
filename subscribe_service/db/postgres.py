import logging
import uuid
from asyncio import shield
from logging import Logger
from typing import AsyncGenerator

from fastapi import Depends
from sqlalchemy import MetaData
from sqlalchemy.exc import DBAPIError
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import declarative_base

from core.settings import settings


Base = declarative_base(metadata=MetaData())

engine = create_async_engine(settings.postgres.pg_dsn, echo=settings.debug, future=True)
create_async_session = async_sessionmaker(engine, expire_on_commit=False)


def get_logger() -> Logger:
    return logging.getLogger("api")


async def get_session(logger: Logger = Depends(get_logger)) -> AsyncGenerator[AsyncSession, None]:
    session = create_async_session()
    xid = uuid.uuid4()
    try:
        logger.debug("Transaction BEGIN;", extra={"xid": xid})
        yield session
        await session.commit()
        logger.debug("Transaction COMMIT;", extra={"xid": xid})

    except DBAPIError as e:
        await session.rollback()
        logger.error("Transaction ROLLBACK; (Database Error)", extra={"xid": xid})
        raise e

    except Exception:
        await session.rollback()
        logger.debug(f"[{xid}] Transaction ROLLBACK; (Application Error)")
        raise

    finally:
        if session:
            await shield(session.close())
            logger.debug("Connection released to pool")
