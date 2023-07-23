from typing import Annotated
from uuid import UUID

from api.schemas import Film, FullFilm
from api.schemas.user import User
from api.utils import PaginateQueryParams
from constants import FilmSort
from fastapi import APIRouter, Depends, HTTPException, Query
from security import security_jwt
from services.film import FilmService, get_film_service
from starlette import status


router = APIRouter()


@router.get(
    '/',
    response_model=list[Film],
    summary="Список фильмов",
    description="Список фильмов с пагинацией, возможностью сортировки по рейтингу фильма "
    "и возможностью фильтрации по жанрам",
)
async def films(
    paginate: Annotated[PaginateQueryParams, Depends(PaginateQueryParams)],
    film_service: Annotated[FilmService, Depends(get_film_service)],
    user: Annotated[dict | None, Depends(security_jwt)],
    sort: FilmSort | None = None,
    genre: str | None = None,
) -> list[Film]:
    """Список фильмов."""
    films = await film_service.filter(
        page_size=paginate.page_size,
        page_number=paginate.page_number,
        sort=sort,
        genre=genre,
    )
    returned_films = [Film.parse_obj(film) for film in films]

    return returned_films


@router.get(
    '/search',
    response_model=list[Film],
    summary="Поиск по фильмам",
    description="Полнотекстовый поиск по фильмам. "
    "Ищет по полям 'title', 'description', 'actors_names', 'director', 'writers_names' и 'genre'",
)
async def film_search(
    paginate: Annotated[PaginateQueryParams, Depends(PaginateQueryParams)],
    film_service: Annotated[FilmService, Depends(get_film_service)],
    user: Annotated[dict | None, Depends(security_jwt)],
    query: Annotated[str | None, Query(max_length=255)] = None,
) -> list[Film]:
    """Поиск по фильмам."""
    films = await film_service.filter(
        page_size=paginate.page_size,
        page_number=paginate.page_number,
        query=query,
    )
    returned_films = [Film.parse_obj(film) for film in films]

    return returned_films


# Внедряем FilmService с помощью Depends(get_film_service)
@router.get(
    '/{film_id}',
    response_model=FullFilm,
    summary="Фильма по ID",
    description="Получение полной информации по фильму по его ID",
)
async def film_details(
    film_id: UUID,
    film_service: Annotated[FilmService, Depends(get_film_service)],
    raw_user: Annotated[dict | None, Depends(security_jwt)],
) -> FullFilm:
    """Страница фильма."""

    film = await film_service.get_by_id(film_id)
    if not film:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail='film not found'
        )

    user = User.parse_obj(raw_user)
    if film.new and not user.is_subscriber:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail='Permission denied'
        )

    returned_film = FullFilm(
        uuid=film.uuid,
        title=film.title,
        imdb_rating=film.imdb_rating,
        description=film.description,
        genres=film.genre,
        cast=[*film.actors_names, *film.writers_names],
        new=film.new,
    )

    return returned_film
