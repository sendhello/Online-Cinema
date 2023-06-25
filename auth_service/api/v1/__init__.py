from fastapi.routing import APIRouter

from .user import router as user_router

router = APIRouter()
router.include_router(user_router, prefix='/users', tags=['users'])
