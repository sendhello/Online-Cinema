from fastapi.routing import APIRouter

from .auth import router as auth_router
from .profile import router as profile_router

router = APIRouter()
router.include_router(auth_router, prefix='/auth', tags=['auth'])
router.include_router(profile_router, prefix='/profile', tags=['profile'])
