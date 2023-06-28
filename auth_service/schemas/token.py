import orjson
from async_fastapi_jwt_auth import AuthJWT
from .user import UserInDB

from .base_model import Model


class Tokens(Model):
    access_token: str
    refresh_token: str

    @classmethod
    async def create(cls, authorize: AuthJWT, user: UserInDB) -> 'Tokens':
        user_claims = orjson.loads(user.json())
        access_token = await authorize.create_access_token(
            subject=str(user.id), user_claims=user_claims
        )
        refresh_token = await authorize.create_refresh_token(
            subject=str(user.id), user_claims=user_claims
        )

        return cls(access_token=access_token, refresh_token=refresh_token)
