import logging
import traceback

import asyncpg
import httpx
from fastapi.requests import Request
from fastapi.responses import JSONResponse
from starlette import status

from core.settings import settings


logger = logging.getLogger("api")


async def exception_traceback_middleware(request: Request, call_next):
    try:
        return await call_next(request)

    except (httpx.ConnectTimeout, httpx.ConnectError, httpx.ReadTimeout, httpx.ReadError) as e:
        logger.info(f"Connection to {e.request.url} timed out")
        detail = {"message": "Service unavailable"}
        if settings.show_traceback:
            detail["cause"] = {
                "url": str(e.request.url),
                "method": e.request.method,
                "error": str(e.__class__.__name__),
            }
        return JSONResponse(detail, status.HTTP_503_SERVICE_UNAVAILABLE)

    except asyncpg.TooManyConnectionsError:
        return JSONResponse({"message", "Bad Gateway"}, status.HTTP_502_BAD_GATEWAY)

    except Exception as exc:
        logger.error(f"{exc.__class__.__name__}: {exc}", exc_info=True)
        return JSONResponse(
            {"message": f"{exc.__class__.__name__}: {exc}", "traceback": traceback.format_exception(exc)},
            status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
