from http import HTTPStatus

from async_fastapi_jwt_auth import AuthJWT
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.encoders import jsonable_encoder
from models import User
from schemas import Tokens, UserCreate, UserInDB, UserLogin
from security import PART_PROTECTED, PROTECTED, REFRESH_PROTECTED
from sqlalchemy.exc import IntegrityError
from starlette.status import HTTP_409_CONFLICT
import uuid

from async_fastapi_jwt_auth import AuthJWT
from async_fastapi_jwt_auth.exceptions import AuthJWTException
from constants import ANONYMOUS

router = APIRouter()


@router.post('/signup', response_model=UserInDB, status_code=status.HTTP_201_CREATED)
async def create_user(user_create: UserCreate) -> UserInDB:
    user_dto = jsonable_encoder(user_create)
    try:
        user = await User.create(**user_dto)

    except IntegrityError:
        raise HTTPException(
            status_code=HTTP_409_CONFLICT,
            detail='User with such login is registered already',
        )

    return user


@router.post("/login", response_model=Tokens, status_code=status.HTTP_200_OK)
async def login(user_login: UserLogin, authorize: AuthJWT = Depends()) -> Tokens:
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
    tokens = await Tokens.create(authorize, user)
    return tokens


@router.post('/refresh', dependencies=REFRESH_PROTECTED)
async def refresh(authorize: AuthJWT = REFRESH_PROTECTED[0]):
    user_claim = await authorize.get_raw_jwt()
    current_user = UserInDB.parse_obj(user_claim)
    tokens = await Tokens.create(authorize, current_user)
    return tokens


@router.get('/user', response_model=UserInDB, dependencies=PROTECTED)
async def user(authorize: AuthJWT = PROTECTED[0]):
    user_claim = await authorize.get_raw_jwt()
    current_user = UserInDB.parse_obj(user_claim)
    return current_user


@router.get('/partially-protected', response_model=UserInDB, dependencies=PART_PROTECTED)
async def partially_protected(authorize: AuthJWT = PART_PROTECTED[0]):
    anonymous = UserInDB(
        id=uuid.uuid4(),
        first_name=ANONYMOUS,
        last_name=ANONYMOUS,
    )
    user_claim = await authorize.get_raw_jwt()
    current_user = UserInDB.parse_obj(user_claim) if user_claim else None
    return current_user or anonymous
