import uuid

from async_fastapi_jwt_auth import AuthJWT
from constants import ANONYMOUS
from fastapi import APIRouter, HTTPException
from fastapi.encoders import jsonable_encoder
from models import History, User
from schemas import HistoryInDB, UserChangePassword, UserInDB, UserUpdate
from security import PART_PROTECTED, PROTECTED
from sqlalchemy.exc import IntegrityError
from starlette import status

router = APIRouter()


@router.get('/', response_model=UserInDB, dependencies=PROTECTED)
async def user(authorize: AuthJWT = PROTECTED[0]):
    user_claim = await authorize.get_raw_jwt()
    current_user = UserInDB.parse_obj(user_claim)
    return current_user


@router.get('/history', response_model=list[HistoryInDB], dependencies=PROTECTED)
async def history(authorize: AuthJWT = PROTECTED[0]) -> list[History]:
    user_claim = await authorize.get_raw_jwt()
    current_user = UserInDB.parse_obj(user_claim)
    histories = await History.get_by_user_id(user_id=current_user.id)
    return histories


@router.post('/update', response_model=UserInDB, dependencies=PROTECTED)
async def change_user(user_update: UserUpdate, authorize: AuthJWT = PROTECTED[0]):
    user_claim = await authorize.get_raw_jwt()
    current_user = UserInDB.parse_obj(user_claim)

    db_user = await User.get_by_login(username=current_user.login)
    if db_user is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail='Incorrect userdata'
        )

    if not db_user.check_password(user_update.current_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail='Incorrect password'
        )

    user_dto = jsonable_encoder(user_update)
    user_dto.pop('current_password')
    try:
        user = await db_user.update(**user_dto)

    except IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail='User with such login is registered already',
        )

    return user


@router.post('/change_password', response_model=UserInDB, dependencies=PROTECTED)
async def change_password(
    user_change_password: UserChangePassword, authorize: AuthJWT = PROTECTED[0]
):
    user_claim = await authorize.get_raw_jwt()
    current_user = UserInDB.parse_obj(user_claim)

    db_user = await User.get_by_login(username=current_user.login)
    if db_user is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail='Incorrect userdata'
        )

    if not db_user.check_password(user_change_password.current_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail='Incorrect password'
        )

    user_dto = jsonable_encoder(user_change_password)
    user_dto.pop('current_password')
    try:
        user = await db_user.change_password(user_change_password.new_password)

    except IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail='User with such login is registered already',
        )

    return user
