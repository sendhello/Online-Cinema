from db.postgres import AsyncSession, get_session
from fastapi import APIRouter, Depends, status
from schemas import UserCreate, UserInDB

router = APIRouter()


@router.post("/signup", response_model=UserInDB, status_code=status.HTTP_201_CREATED)
async def create_user(
    user_create: UserCreate, db: AsyncSession = Depends(get_session)
) -> UserInDB:
    user_dto = jsonable_encoder(user_create)
    user = User(**user_dto)
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user
