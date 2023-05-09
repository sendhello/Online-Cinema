from http import HTTPStatus

from fastapi import APIRouter, Depends, HTTPException, Query

from constants import GenreSort
from models.film import Genre
from services.genre import GenreService, get_genre_service

router = APIRouter()


@router.get('/', response_model=list[Genre])
async def genre_list(
        page_size: int = Query(50, ge=1),
        page_number: int = Query(1, ge=1),
        sort: GenreSort | None = Query(None),
        genre: str = Query(None),
        genre_service: GenreService = Depends(get_genre_service)
) -> list[Genre]:
    """
    Поиск по фильмам.
    """

    genres_es = await genre_service.get_genres(
        item_id=genre,
        page_size=page_size, page_number=page_number,
        sort=sort)

    genres = [Genre.parse_obj(genre.dict(by_alias=True)) for genre in genres_es]

    return genres


@router.get('/search', response_model=list[Genre])
async def genre_search(
    page_size: int = Query(50, ge=1),
    page_number: int = Query(1, ge=1),
    sort: GenreSort | None = Query(None),
    query: str | None = Query(None),
    genre_service: GenreService = Depends(get_genre_service)
) -> list[Genre]:

    genres = await genre_service.get_genres(page_size=page_size, page_number=page_number, sort=sort, query=query)
    return [Genre.parse_obj(genre.dict(by_alias=True)) for genre in genres]


@router.get('/{genre_id}', response_model=Genre)
async def genre_info(
        genre_id: str,
        genre_service: GenreService = Depends(get_genre_service)
) -> Genre:
    """
    Список фильмов.
    """
    genre = await genre_service.get_genre_by_id(genre_id)
    if not genre:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND,
                            detail=f'genre id {genre_id} not found')
    return Genre.parse_obj(genre.dict(by_alias=True))
