import pytest
from typing import Callable
from functional.testdata.persons_data import (
    PERSONS_DATA,
    PERSON_BY_UUID_DATA,
    PERSON_FILMS_BY_UUID_DATA,
    PERSON_SEARCH_DATA,
)


@pytest.mark.parametrize(
    'es_data, expected_data',
    PERSONS_DATA,
)
@pytest.mark.asyncio
async def test_get_all_persons(
        redis_client,
        es_write_data: Callable,
        service_get_data: Callable,
        es_data: list[dict],
        expected_data: str,
):
    """
    Тест: получение всех персоналий
    /api/v1/persons
    """
    await es_write_data(es_data, 'persons')

    response = await service_get_data('persons/')

    assert response.status == 200, response.body
    assert response.body == expected_data


@pytest.mark.parametrize(
    'uuid_person, es_data, expected_data',
    PERSON_BY_UUID_DATA,
)
@pytest.mark.asyncio
async def test_get_person(
        redis_client,
        es_write_data: Callable,
        service_get_data: Callable,
        uuid_person, es_data, expected_data
):
    """
    Тест: поиск по uuid
    /api/v1/persons/<uuid_person>
    """
    await es_write_data(es_data, 'persons')

    response = await service_get_data(f'persons/{uuid_person}')

    assert response.status == 200, response.body
    assert response.body == expected_data


@pytest.mark.parametrize(
    'uuid_person, es_data, expected_data',
    PERSON_FILMS_BY_UUID_DATA,
)
@pytest.mark.asyncio
async def test_get_person_film(
        redis_client, es_write_data, service_get_data,
        uuid_person, es_data, expected_data,
):
    """
    Тест: получение фильмов персоналии
    /api/v1/persons/<uuid_person>/film
    """
    await es_write_data(es_data['persons'], 'persons')
    await es_write_data(es_data['movies'], 'movies')

    response = await service_get_data(f'persons/{uuid_person}/film')

    assert response.status == 200, response.body
    assert response.body == expected_data


@pytest.mark.parametrize(
    'params, es_data, expected_data',
    PERSON_SEARCH_DATA,
)
@pytest.mark.asyncio
async def test_get_person_search(
        redis_client, es_write_data, service_get_data,
        expected_data, es_data, params,
):
    """
    Тест: Поиск по имени
    /api/v1/persons/search/
    """
    await es_write_data(es_data['persons'], 'persons')
    await es_write_data(es_data['movies'], 'movies')

    response = await service_get_data(f'persons/search', params=params)

    assert response.status == 200, response.body
    assert response.body == expected_data
