from contextlib import asynccontextmanager

from api import router as api_router
from core.config import settings
from db import postgres, redis_db
from fastapi import FastAPI
from fastapi.responses import ORJSONResponse
from redis.asyncio import Redis


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Импорт моделей необходим для их автоматического создания
    from models import History, Role, User  # noqa

    await postgres.create_database()
    redis_db.redis = Redis(
        host=settings.redis_host, port=settings.redis_port, db=0, decode_responses=True
    )
    yield

    await postgres.purge_database()
    await redis_db.redis.close()


app = FastAPI(
    lifespan=lifespan,
    title=settings.project_name,
    description="Сервис аутентификации и авторизации",
    version="1.0.0",
    docs_url="/api/openapi",
    openapi_url="/api/openapi.json",
    default_response_class=ORJSONResponse,
)

app.include_router(api_router, prefix="/api")
