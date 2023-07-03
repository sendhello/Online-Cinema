from fastapi.routing import APIRouter

from .auth import router as auth_router
from .profile import router as profile_router
from .roles import router as roles_router
from .users import router as users_router

router = APIRouter()
router.include_router(auth_router, prefix='/auth', tags=['auth'])
router.include_router(profile_router, prefix='/profile', tags=['profile'])
router.include_router(roles_router, prefix='/roles', tags=['roles'])
router.include_router(users_router, prefix='/users', tags=['users'])
