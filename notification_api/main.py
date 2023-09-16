from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.responses import ORJSONResponse

from api.v1 import notification, task
from core.config import project_settings, rabbit_settings
from gateways.rabbitmq import RabbitGateway
from handlers.rabbitmq import rmq_handler


@asynccontextmanager
async def lifespan(app: FastAPI):
    rabbit_gateway = RabbitGateway()
    await rabbit_gateway.startup()
    await rabbit_gateway.create_queue_listener(
        queue_name=rabbit_settings.rabbitmq_source_queue_name,
        callback_worker=rmq_handler,
    )
    yield

    await rabbit_gateway.shutdown()


app = FastAPI(
    lifespan=lifespan,
    title=project_settings.project_name,
    docs_url="/api/notification/openapi",
    openapi_url="/api/notification/openapi.json",
    default_response_class=ORJSONResponse,
)

app.include_router(notification.router, prefix="/api/v1/notification")
app.include_router(task.router, prefix="/api/v1/task")
