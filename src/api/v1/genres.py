from http import HTTPStatus
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from api.utils import PaginateQueryParams
from api.schemas.genre import Genre
from services.genre import GenreService, get_genre_service
from typing import Annotated

router = APIRouter()


@router.get(
    '/',
    response_model=list[Genre],
    summary="Список жанров",
    description="Получение списка всех жанров",
)
async def genres(
        paginate: Annotated[PaginateQueryParams, Depends(PaginateQueryParams)],
        genre_service: Annotated[GenreService, Depends(get_genre_service)],
) -> list[Genre]:
    """Список жанров.
    """
    genres = await genre_service.filter(
        page_size=paginate.page_size,
        page_number=paginate.page_number,
    )
    returned_genres = [Genre.parse_obj(genre) for genre in genres]

    return returned_genres


@router.get(
    '/{genre_id}',
    response_model=Genre,
    summary="Жанр по ID",
    description="Получение жанра по его ID",
)
async def genre_details(
        genre_id: UUID,
        genre_service: Annotated[GenreService, Depends(get_genre_service)],
) -> Genre:
    """Страница жанра.
    """
    genre = await genre_service.get_by_id(genre_id)
    if not genre:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='genre not found')

    return Genre.parse_obj(genre)
