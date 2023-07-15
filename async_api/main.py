from contextlib import asynccontextmanager

from api import router as api_router
from core.settings import settings
from core.tracer import configure_tracer
from db import elastic, redis
from elasticsearch import AsyncElasticsearch
from fastapi import FastAPI
from fastapi.responses import ORJSONResponse
from middleware import required_request_id
from opentelemetry.instrumentation.elasticsearch import ElasticsearchInstrumentor
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.redis import RedisInstrumentor
from redis.asyncio import Redis


@asynccontextmanager
async def lifespan(app: FastAPI):
    redis.redis = Redis(host=settings.redis_host, port=settings.redis_port)
    elastic.es = AsyncElasticsearch(
        hosts=[f'http://{settings.elastic_host}:{settings.elastic_port}']
    )
    yield

    await redis.redis.close()
    await elastic.es.close()


app = FastAPI(
    lifespan=lifespan,
    title=settings.project_name,
    description="Информация о фильмах, жанрах и людях, участвовавших в создании произведения",
    version="1.0.0",
    docs_url='/api/api/openapi',
    openapi_url='/api/api/openapi.json',
    default_response_class=ORJSONResponse,
)

if settings.jaeger_trace:
    # Отправка телеметрии в Jaeger
    configure_tracer()
    FastAPIInstrumentor.instrument_app(app)
    ElasticsearchInstrumentor().instrument()
    RedisInstrumentor().instrument()

    if not settings.debug:
        # Делаем Header-поле X-Request-Id обязательным
        app.middleware('http')(required_request_id)

app.include_router(api_router, prefix='/api')
