import pytest
from functional.testdata.genres_data import GENRE_DATA, GENRES_LIST_DATA


pytest_mark = pytest.mark.asyncio


@pytest.mark.parametrize(
    'es_data, expected_data',
    GENRES_LIST_DATA,
)
@pytest_mark
async def test_get_all_genres(
        redis_client, es_write_data, service_get_data,
        es_data, expected_data,
):
    """
    Тест: получение всех персоналий
    /api/v1/persons
    """
    await es_write_data(es_data, 'genres')

    response = await service_get_data('genres/')

    assert response.status == 200, response.body
    assert response.body == expected_data


@pytest.mark.parametrize(
    'genre_id, es_data, expected_data',
    GENRE_DATA,
)
@pytest_mark
async def test_get_genre(
        redis_client, es_write_data, service_get_data,
        genre_id, es_data, expected_data
):
    """
    Тест: поиск по uuid
    /api/v1/persons/<uuid_person>
    """
    await es_write_data(es_data, 'genres')

    response = await service_get_data(f'genres/{genre_id}')

    assert response.status == 200, response.body
    assert response.body == expected_data
