import uuid

from async_fastapi_jwt_auth import AuthJWT
from async_fastapi_jwt_auth.exceptions import AuthJWTException
from constants import ANONYMOUS
from fastapi import Depends
from fastapi.exceptions import HTTPException
from fastapi.security.http import HTTPBearer
from schemas import Tokens, UserInDB


async def full_protected(
    authorize: AuthJWT = Depends(), _: str = Depends(HTTPBearer(auto_error=False))
) -> AuthJWT:
    try:
        await authorize.jwt_required()

    except AuthJWTException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)

    return authorize


async def partial_protected(
    authorize: AuthJWT = Depends(), _: str = Depends(HTTPBearer(auto_error=False))
) -> AuthJWT:
    try:
        await authorize.jwt_optional()

    except AuthJWTException as e:
        raise HTTPException(status_code=e.status_code, detail=str(e))

    return authorize


async def refresh_protected(
    authorize: AuthJWT = Depends(), _: str = Depends(HTTPBearer(auto_error=False))
) -> AuthJWT:
    try:
        await authorize.jwt_refresh_token_required()

    except AuthJWTException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)

    return authorize
