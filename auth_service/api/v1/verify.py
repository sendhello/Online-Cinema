from uuid import uuid4

from async_fastapi_jwt_auth import AuthJWT
from constants import ANONYMOUS
from db.redis_db import get_redis
from fastapi import APIRouter, Depends, Header, HTTPException
from fastapi.security import HTTPAuthorizationCredentials
from fastapi.security.http import HTTPBearer
from models import Rules
from pydantic import EmailStr
from redis.asyncio import Redis
from schemas import RoleInDB, Rule, UserInDB
from security import PART_PROTECTED
from services.rules import rules
from starlette import status


router = APIRouter()


@router.post('/verify', response_model=UserInDB, dependencies=PART_PROTECTED)
async def verify(
    checked_entity: Rule | None,
    user_agent: str = Header(default=None),
    authorize: AuthJWT = Depends(),
    redis: Redis = Depends(get_redis),
    credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer(auto_error=False)),
) -> dict:
    anonymous = UserInDB(
        id=uuid4(),
        login=ANONYMOUS,
        email=EmailStr(f"{ANONYMOUS}@{ANONYMOUS}.email"),
        first_name=ANONYMOUS,
        last_name=ANONYMOUS,
    )
    user_claim = await authorize.get_raw_jwt()
    current_user = UserInDB.parse_obj(user_claim) if user_claim else anonymous

    if checked_entity is None:
        return current_user

    if current_user.role is None:
        current_user.role = RoleInDB(
            id=uuid4(), title=ANONYMOUS, rules=[Rules.anonymous_rules]
        )

    for text_rule in current_user.role.rules:
        rule_model = rules.get(text_rule)
        if checked_entity in rule_model.rules:
            return current_user

    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN, detail='Permission denied'
    )
