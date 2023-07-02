import uuid
from hashlib import md5
from http import HTTPStatus

from async_fastapi_jwt_auth import AuthJWT
from constants import ANONYMOUS
from core.settings import settings
from db.redis_db import get_redis
from fastapi import APIRouter, Depends, Header, HTTPException
from fastapi.encoders import jsonable_encoder
from models import User
from redis.asyncio import Redis
from schemas import Tokens, UserCreate, UserInDB, UserLogin
from security import PART_PROTECTED, PROTECTED, REFRESH_PROTECTED
from sqlalchemy.exc import IntegrityError
from starlette import status

router = APIRouter()


@router.post('/signup', response_model=UserInDB, status_code=status.HTTP_201_CREATED)
async def create_user(user_create: UserCreate) -> UserInDB:
    user_dto = jsonable_encoder(user_create)
    try:
        user = await User.create(**user_dto)

    except IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail='User with such login is registered already',
        )

    return user


@router.post('/login', response_model=Tokens)
async def login(
    user_login: UserLogin,
    user_agent: str = Header(default=None),
    authorize: AuthJWT = Depends(),
) -> Tokens:
    db_user = await User.get_by_login(username=user_login.login)
    if db_user is None:
        raise HTTPException(
            status_code=HTTPStatus.UNAUTHORIZED, detail='Incorrect username or password'
        )

    if not db_user.check_password(user_login.password):
        raise HTTPException(
            status_code=HTTPStatus.UNAUTHORIZED, detail='Incorrect username or password'
        )

    user = UserInDB.from_orm(db_user)
    tokens = await Tokens.create(authorize, user, user_agent)
    return tokens


@router.post('/logout', dependencies=PROTECTED)
async def logout(
    user_agent: str = Header(default=None),
    authorize: AuthJWT = Depends(),
    redis: Redis = Depends(get_redis),
) -> dict:
    access_key = await authorize.get_jwt_subject()
    access_token_expires = settings.authjwt_access_token_expires
    await redis.setex(
        name=access_key, time=access_token_expires, value=authorize._token
    )

    user_claim = await authorize.get_raw_jwt()
    current_user = UserInDB.parse_obj(user_claim)
    user_agent_hash = md5(user_agent.encode()).hexdigest()
    refresh_key = f'refresh.{current_user.id}.{user_agent_hash}'
    await redis.delete(refresh_key)
    return {}


@router.post('/refresh', dependencies=REFRESH_PROTECTED)
async def refresh(
    user_agent: str = Header(default=None),
    authorize: AuthJWT = REFRESH_PROTECTED[0],
    redis: Redis = Depends(get_redis),
):
    old_refresh_key = await authorize.get_jwt_subject()
    await redis.delete(old_refresh_key)

    user_claims = await authorize.get_raw_jwt()
    current_user = UserInDB.parse_obj(user_claims)
    tokens = await Tokens.create(
        authorize=authorize, user=current_user, user_agent=user_agent
    )
    return tokens


@router.get('/user', response_model=UserInDB, dependencies=PROTECTED)
async def user(authorize: AuthJWT = PROTECTED[0]):
    user_claim = await authorize.get_raw_jwt()
    current_user = UserInDB.parse_obj(user_claim)
    return current_user


@router.get(
    '/partially-protected', response_model=UserInDB, dependencies=PART_PROTECTED
)
async def partially_protected(authorize: AuthJWT = PART_PROTECTED[0]):
    anonymous = UserInDB(
        id=uuid.uuid4(),
        first_name=ANONYMOUS,
        last_name=ANONYMOUS,
    )
    user_claim = await authorize.get_raw_jwt()
    current_user = UserInDB.parse_obj(user_claim) if user_claim else None
    return current_user or anonymous
