from uuid import UUID

from async_fastapi_jwt_auth import AuthJWT
from constants import ANONYMOUS
from fastapi import APIRouter, HTTPException
from fastapi.encoders import jsonable_encoder
from models import History, User, Role
from starlette import status
from schemas import HistoryInDB, UserChangePassword, UserWithRole, UserUpdate, RoleInDB, RoleUpdate, RoleDelete, RoleCreate
from security import PART_PROTECTED, PROTECTED
from sqlalchemy.exc import IntegrityError
from starlette import status

router = APIRouter()


@router.get('/', response_model=list[UserWithRole], dependencies=PROTECTED)
async def get_users() -> list[User]:
    users = await User.get_all()
    return users


@router.get('/{id}', response_model=UserWithRole, dependencies=PROTECTED)
async def get_user(id: UUID) -> User:
    user = await User.get_by_id(id_=id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='User doesn\'t exists')

    return user


@router.delete('/{id}', response_model=UserWithRole, dependencies=PROTECTED)
async def delete_user(id: UUID) -> User:
    user = await User.get_by_id(id_=id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='User doesn\'t exists')

    return await user.delete()


@router.post('/{id}/set_role', response_model=UserWithRole, dependencies=PROTECTED)
async def set_role(id: UUID, role_id: UUID) -> User:
    user = await User.get_by_id(id_=id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='User doesn\'t exists')

    role = await Role.get_by_id(id_=role_id)
    if not role:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Role doesn\'t exists')

    user.role_id = role_id
    await user.save()

    return user


@router.post('/{id}/remove_role', response_model=UserWithRole, dependencies=PROTECTED)
async def remove_role(id: UUID) -> User:
    user = await User.get_by_id(id_=id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='User doesn\'t exists')

    user.role_id = None
    await user.save()

    return user
