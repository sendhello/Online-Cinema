from http import HTTPStatus
from typing import Annotated
from uuid import UUID
from api.utils import PaginateQueryParams

from fastapi import APIRouter, Depends, HTTPException, Query

from api.schemas import Film, FullFilm
from constants import FilmSort
from services.film import FilmService, get_film_service

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
        sort: FilmSort | None = None,
        genre: str | None = None,
) -> list[Film]:
    """Список фильмов.
    """
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
        query: Annotated[str | None, Query(max_length=255)] = None,
) -> list[Film]:
    """Поиск по фильмам.
    """
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
    description="Получение польной информации по фильму по его ID",
)
async def film_details(
        film_id: UUID,
        film_service: Annotated[FilmService, Depends(get_film_service)],
) -> FullFilm:
    """Страница фильма.
    """
    film = await film_service.get_by_id(film_id)
    if not film:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='film not found')

    returned_film = FullFilm(
        uuid=film.uuid,
        title=film.title,
        imdb_rating=film.imdb_rating,
        description=film.description,
        genres=film.genre,
        cast=[*film.actors_names, *film.writers_names],
    )

    return returned_film
