import traceback
from logging import Logger

import httpx
import sentry_sdk
from fastapi import Request, Response, status
from fastapi.responses import JSONResponse

from core.settings import Settings


async def connection_timeout_handler(
    settings: Settings,
    logger: Logger,
    request: Request,
    exc: httpx.ConnectTimeout | httpx.ConnectError,
) -> Response:
    sentry_sdk.capture_exception(exc)
    logger.error(exc.args, exc_info=True)
    detail = {
        "message": exc.args[0],
        "cause": {
            "url": str(request.url),
            "method": request.method,
            "error": str(exc.__class__.__name__),
        },
    }
    if settings.show_traceback:
        detail["traceback"] = traceback.format_exc()

    return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content=detail)


async def http_status_handler(
    settings: Settings, logger: Logger, request: Request, exc: httpx.HTTPStatusError
) -> Response:
    sentry_sdk.capture_exception(exc)
    data = {
        "message": exc.args[0],
        "cause": {
            "error": str(exc.__class__.__name__),
            "method": request.method,
            "url": str(request.url),
        },
    }
    if settings.debug and request.method == "POST":
        logger.error(exc.args, exc_info=True, extra={"payload": exc.request.content})
    else:
        logger.error(exc.args, exc_info=True)

    return JSONResponse(status_code=exc.response.status_code, content=data)


async def default_handler(settings: Settings, logger: Logger, request: Request, exc: Exception) -> Response:
    sentry_sdk.capture_exception(exc)
    logger.error(exc.args, exc_info=True)
    data = {
        "message": exc.args[0],
        "cause": {
            "error": str(exc.__class__.__name__),
            "method": request.method,
            "url": str(request.url),
        },
    }
    if settings.show_traceback:
        data["traceback"] = traceback.format_exc()

    return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content=data)
