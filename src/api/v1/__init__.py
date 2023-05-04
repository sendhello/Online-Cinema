from fastapi.routing import APIRouter

from .films import router as films_router

router = APIRouter()
router.include_router(films_router, prefix='/films', tags=['films'])
