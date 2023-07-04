from uuid import UUID

from async_fastapi_jwt_auth import AuthJWT
from constants import ANONYMOUS
from fastapi import APIRouter, HTTPException
from fastapi.encoders import jsonable_encoder
from models import History, User, Role
from starlette import status
from schemas import HistoryInDB, UserChangePassword, UserInDB, UserUpdate, RoleInDB, RoleUpdate, RoleDelete, RoleCreate
from security import PART_PROTECTED, PROTECTED
from sqlalchemy.exc import IntegrityError
from starlette import status
from models import Rules

router = APIRouter()


@router.get('/', response_model=list[RoleInDB], dependencies=PROTECTED)
async def get_roles() -> list[Role]:
    roles = await Role.get_all()
    return roles


@router.post('/', response_model=RoleInDB, dependencies=PROTECTED)
async def create_role(role_in: RoleCreate) -> Role:
    role_dto = jsonable_encoder(role_in)
    try:
        role = await Role.create(**role_dto)

    except IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail='Role with such title already exists',
        )

    return role


@router.get('/{id}', response_model=RoleInDB, dependencies=PROTECTED)
async def get_role(id: UUID) -> Role:
    role = await Role.get_by_id(id_=id)
    if not role:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Role doesn\'t exists')

    return role


@router.put('/{id}', response_model=RoleInDB, dependencies=PROTECTED)
async def update_role(id: UUID, role_in: RoleUpdate) -> Role:
    role = await Role.get_by_id(id_=id)
    if not role:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Role doesn\'t exists')

    role_dto = jsonable_encoder(role_in)
    role = await role.update(**role_dto)
    return role


@router.delete('/{id}', response_model=RoleInDB, dependencies=PROTECTED)
async def delete_role(id: UUID) -> Role:
    role = await Role.get_by_id(id_=id)
    if not role:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Role doesn\'t exists')

    return await role.delete()


@router.post('/{id}/set_rule', response_model=RoleInDB, dependencies=PROTECTED)
async def set_rule(id: UUID, rule: Rules) -> Role:
    role = await Role.get_by_id(id_=id)
    if not role:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Role doesn\'t exists')

    current_rules = role.rules
    if rule.value in current_rules:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail='Role has this rule already')

    role.rules = [*current_rules, rule.value]
    await role.save()

    return role


@router.post('/{id}/remove_rule', response_model=RoleInDB, dependencies=PROTECTED)
async def set_rule(id: UUID, rule: Rules) -> Role:
    role = await Role.get_by_id(id_=id)
    if not role:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Role doesn\'t exists')

    current_rules = [*role.rules]
    if rule.value not in current_rules:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Role doesn\'t have this rule')

    current_rules.remove(rule.value)
    role.rules = current_rules
    await role.save()

    return role
