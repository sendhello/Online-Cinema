from fastapi import FastAPI
from fastapi.responses import ORJSONResponse
from httpx import ConnectError, ConnectTimeout, HTTPStatusError
from api.v1.api import router
from core.settings import settings
from middleware.exceptions import exception_traceback_middleware
from handlers.api import connection_timeout_handler, http_status_handler, default_handler
from logging import getLogger
from functools import partial
from core.sentry import connect_sentry


logger = getLogger(__name__)
if settings.sentry_dsn:
    connect_sentry(settings)


app = FastAPI(
    title=settings.project_name,
    docs_url="/api/subscribe/openapi",
    openapi_url="/api/subscribe/openapi.json",
    default_response_class=ORJSONResponse,
)

if settings.show_traceback:
    app.middleware("http")(exception_traceback_middleware)

for exc in (ConnectTimeout, ConnectError):
    app.exception_handler(exc)(partial(connection_timeout_handler, settings, logger))
app.exception_handler(HTTPStatusError)(partial(http_status_handler, settings, logger))
app.exception_handler(Exception)(partial(default_handler, settings, logger))

app.include_router(router, prefix="/api/v1")
