from http import HTTPStatus

from fastapi import APIRouter, Depends, HTTPException, Query

from api.schemas.film import Film
from api.schemas.person import PersonDescription
from constants import PersonSort
from models.person import Person
from services.person import PersonService, get_person_service

router = APIRouter()


@router.get('/', response_model=list[Person])
async def person_list(
        page_size: int = Query(50),
        page_number: int = Query(1),
        sort: PersonSort | None = Query(None),
        person_id: str = Query(None),
        person_service: PersonService = Depends(get_person_service)
) -> list[Person]:
    persons = await person_service.get_persons(
        page_size=page_size, page_number=page_number, sort=sort, item_id=person_id)
    return [Person.parse_obj(person.dict(by_alias=True)) for person in persons]


@router.get('/search', response_model=list[Person])
async def person_search(
        page_size: int = Query(10),
        page_number: int = Query(1),
        sort: PersonSort | None = Query(None),
        query: str = Query(None),
        person_service: PersonService = Depends(get_person_service)
) -> list[Person]:
    persons = await person_service.get_persons(page_size=page_size, page_number=page_number, sort=sort, query=query)
    return [Person.parse_obj(person.dict(by_alias=True)) for person in persons]


@router.get('/{person_id}', response_model=PersonDescription)
async def person_details(person_id: str,
                         person_service: PersonService = Depends(get_person_service)
                         ) -> PersonDescription:
    person = await person_service.get_person_by_id(person_id)
    if not person:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='Person not found')
    return PersonDescription.parse_obj(person.dict(by_alias=True))


@router.get('/{person_id}/film', response_model=list[Film])
async def list_film_by_person(
        person_id: str,
        person_service: PersonService = Depends(get_person_service)
) -> list[Film]:

    films = await person_service.get_person_films_by_id(person_id=person_id)
    return [Film(uuid=film.id, title=film.title, imdb_rating=film.imdb_rating) for film in films]
