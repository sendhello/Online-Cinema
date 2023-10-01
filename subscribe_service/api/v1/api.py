from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.requests import Request
from sqlalchemy.exc import OperationalError
from sqlalchemy.sql import text

from api.v1.endpoints.payment import router as payment_router
from api.v1.endpoints.subscribe import router as subscribe_router
from core.settings import settings
from db.postgres import create_async_session
from schemas.user import User
from security import security_jwt


router = APIRouter()


@router.get("/")
async def index():
    status = {
        settings.project_name: True,
        "db": True,
    }

    try:
        async with create_async_session() as session:
            await session.execute(text("SELECT 1"))

    except OperationalError:
        status["db"] = False

    return status


@router.get("/me/", response_model=User)
async def me(request: Request, user: Annotated[dict | None, Depends(security_jwt)]):
    return user


router.include_router(subscribe_router, prefix="/subscribe", tags=["Subscribe"])
router.include_router(payment_router, prefix="/payments", tags=["Payment"])
