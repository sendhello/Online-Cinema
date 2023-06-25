from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.responses import ORJSONResponse
from redis.asyncio import Redis

from api import router as api_router
from core.config import app_settings
from db import redis_db, postgres


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Импорт моделей необходим для их автоматического создания
    from models.entity import User  # noqa
    await postgres.create_database()
    redis_db.redis = Redis(
        host=app_settings.redis.host,
        port=app_settings.redis.port,
        db=0,
        decode_responses=True
    )
    yield

    await postgres.purge_database()
    await redis_db.redis.close()


app = FastAPI(
    lifespan=lifespan,
    title=app_settings.project_name,
    description="Сервис аутентификации и авторизации",
    version="1.0.0",
    docs_url='/api/openapi',
    openapi_url='/api/openapi.json',
    default_response_class=ORJSONResponse,
)

app.include_router(api_router, prefix='/api')
