from typing import Annotated

from fastapi import Query

from api.schemas import PersonFilm
from models.person import Person
from services.film import FilmService


class PaginateQueryParams:
    """Dependency class to parse pagination query params.
    """
    def __init__(
        self,
        page_number: Annotated[int, Query(
            title="Номер страницы",
            description="Номер возвращаемой страницы",
            ge=1,
        )] = 1,
        page_size: Annotated[int, Query(
            title="Размер страницы",
            description="Число элементов на странице",
            ge=1,
            le=500,
        )] = 50,
    ):
        self.page_number = page_number
        self.page_size = page_size


async def get_person_films(
        page_size: int,
        page_number: int,
        film_service: FilmService,
        person: Person,
) -> list[PersonFilm]:
    films = await film_service.filter(
        page_size=page_size,
        page_number=page_number,
        person_id=person.uuid,
    )

    person_films = []
    for film in films:
        roles = []
        if person.full_name in film.actors_names:
            roles.append('actors')
        if person.full_name in film.writers_names:
            roles.append('writers')

        person_films.append(
            PersonFilm(
                uuid=film.uuid,
                roles=roles,
            )
        )

    return person_films
