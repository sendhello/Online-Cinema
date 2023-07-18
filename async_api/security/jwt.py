import time

from core.settings import settings
from fastapi import HTTPException, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import jwt
from services.aiohttp import AiohttpClient
from starlette import status


def decode_token(token: str) -> dict | None:
    try:
        decoded_token = jwt.decode(
            token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm]
        )
        return decoded_token if decoded_token['exp'] >= time.time() else None

    except Exception:
        return None


class JWTBearer(HTTPBearer):
    def __init__(self, auto_error: bool = True):
        super().__init__(auto_error=auto_error)

    async def __call__(self, request: Request) -> dict:
        credentials: HTTPAuthorizationCredentials = await super().__call__(request)
        if not credentials:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail='Invalid authorization code.',
            )

        if not credentials.scheme == 'Bearer':
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail='Only Bearer token might be accepted',
            )

        authorization = request.headers.get('Authorization')
        status_code, json_response = await AiohttpClient.query_url(
            url=str(settings.validate_url),
            headers={'Authorization': authorization},
        )

        # В случае недоступности сервиса авторизации - проверяем токен локально
        if status_code == 500:
            decoded_token = self.parse_token(credentials.credentials)
            if not decoded_token:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail='Invalid or expired token',
                )
            return decoded_token

        if status_code == 200:
            return json_response

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=json_response.get('detail', json_response),
        )

    @staticmethod
    def parse_token(jwt_token: str) -> dict | None:
        return decode_token(jwt_token)


security_jwt = JWTBearer()
