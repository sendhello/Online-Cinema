from http import HTTPStatus
from typing import Annotated
from uuid import UUID

from api.schemas import Film, Person, PersonDescription
from api.utils import PaginateQueryParams, get_person_films
from constants import FilmSort
from fastapi import APIRouter, Depends, HTTPException, Query
from security import security_jwt
from services.film import FilmService, get_film_service
from services.person import PersonService, get_person_service


router = APIRouter()


@router.get(
    '/',
    response_model=list[Person],
    summary="Список персон",
    description="Получения списка всех персон",
)
async def persons(
    paginate: Annotated[PaginateQueryParams, Depends(PaginateQueryParams)],
    person_service: Annotated[PersonService, Depends(get_person_service)],
    user: Annotated[dict | None, Depends(security_jwt)],
) -> list[Person]:
    """Список фильмов."""
    persons = await person_service.filter(
        page_size=paginate.page_size,
        page_number=paginate.page_number,
    )

    return [Person.parse_obj(person) for person in persons]


@router.get(
    '/search',
    response_model=list[PersonDescription],
    summary="Поиск по персонам",
    description="Полнотекстовый поиск по персонам",
)
async def person_search(
    paginate: Annotated[PaginateQueryParams, Depends(PaginateQueryParams)],
    person_service: Annotated[PersonService, Depends(get_person_service)],
    film_service: Annotated[FilmService, Depends(get_film_service)],
    user: Annotated[dict | None, Depends(security_jwt)],
    query: Annotated[str | None, Query(max_length=255)] = None,
) -> list[PersonDescription]:
    """Поиск по персонам."""
    result = []

    persons = await person_service.filter(
        page_size=paginate.page_size,
        page_number=paginate.page_number,
        query=query,
    )

    for person in persons:
        person_films = await get_person_films(
            film_service=film_service,
            page_size=paginate.page_size,
            page_number=paginate.page_number,
            person=person,
        )

        result.append(
            PersonDescription(
                uuid=person.uuid,
                full_name=person.full_name,
                films=person_films,
            )
        )

    return result


@router.get(
    '/{person_id}',
    response_model=PersonDescription,
    summary="Фильма по ID",
    description="Получение польной информации по фильму по его ID",
)
async def person_details(
    person_id: UUID,
    paginate: Annotated[PaginateQueryParams, Depends(PaginateQueryParams)],
    person_service: Annotated[PersonService, Depends(get_person_service)],
    film_service: Annotated[FilmService, Depends(get_film_service)],
    user: Annotated[dict | None, Depends(security_jwt)],
) -> PersonDescription:
    """Страница персоны."""
    person = await person_service.get_by_id(person_id)
    if not person:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='person not found')

    person_films = await get_person_films(
        page_size=paginate.page_size,
        page_number=paginate.page_number,
        film_service=film_service,
        person=person,
    )

    return PersonDescription(
        uuid=person.uuid,
        full_name=person.full_name,
        films=person_films,
    )


@router.get(
    '/{person_id}/film',
    response_model=list[Film],
    summary="Фильм по ID персоны",
    description="Получение фильма по ID персоны",
)
async def person_films(
    person_id: UUID,
    paginate: Annotated[PaginateQueryParams, Depends(PaginateQueryParams)],
    person_service: Annotated[PersonService, Depends(get_person_service)],
    film_service: Annotated[FilmService, Depends(get_film_service)],
    user: Annotated[dict | None, Depends(security_jwt)],
    sort: FilmSort | None = None,
) -> list[Film]:
    """Фильмы с персоной."""
    person = await person_service.get_by_id(person_id)
    if not person:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='person not found')

    films = await film_service.filter(
        page_size=paginate.page_size,
        page_number=paginate.page_number,
        sort=sort,
        person_id=person.uuid,
    )

    return [Film.parse_obj(film) for film in films]
