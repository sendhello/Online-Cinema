import pytest
from functional.conftest import create_index
from functional.testdata.genres_data import (
    GENRE_DATA, GENRES_LIST_DATA
)


@pytest.mark.parametrize(
    'es_data, expected_data',
    GENRES_LIST_DATA,
)
@pytest.mark.asyncio
async def test_get_all_genres(
        es_client, service_get_data, es_write_data,
        es_data, expected_data,
):
    """
    Тест: получение всех персоналий
    /api/v1/persons
    """
    await create_index(es_client)
    await es_write_data(es_data, 'genres')

    response = await service_get_data('genres/')

    assert response.status == 200, response.body
    assert response.body == expected_data


@pytest.mark.parametrize(
    'genre_id, es_data, expected_data',
    GENRE_DATA,
)
@pytest.mark.asyncio
async def test_get_genre(
        es_client, service_get_data, es_write_data,
        genre_id, es_data, expected_data
):
    """
    Тест: поиск по uuid
    /api/v1/persons/<uuid_person>
    """
    await create_index(es_client)
    await es_write_data(es_data, 'genres')

    response = await service_get_data(f'genres/{genre_id}')

    assert response.status == 200, response.body
    assert response.body == expected_data
