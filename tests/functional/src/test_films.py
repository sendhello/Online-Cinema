from typing import Callable

import pytest
from pydantic import BaseModel, ValidationError
from pydantic.main import ModelMetaclass

from functional.testdata.fims_data import ES_FILMS_DATA
from functional.utils.models.film import EsFilm, ResponseShortFilm, ResponseFilm


@pytest.mark.parametrize(
    'es_data, url_params, res_status, res_count, res_model, check_model_attrs',
    [
        # Кейс получения всех фильмов
        (
            [EsFilm.create_fake().dict() for _ in range(200)],
            None,
            200,
            50,
            ResponseShortFilm,
            {},
        ),

        # Кейс получения 20 фильмов
        (
            [EsFilm.create_fake().dict() for _ in range(200)],
            {'page_size': 20},
            200,
            20,
            ResponseShortFilm,
            {},
        ),

        # Кейс получения фильмов с 3-й страницы
        (
            [EsFilm.create_fake().dict() for _ in range(200)],
            {'page_number': 3},
            200,
            50,
            ResponseShortFilm,
            {},
        ),

        # Кейс получения фильмов с жанром "Drama"
        (
            [
                *[EsFilm.create_fake(genre=['Action', 'Quest']).dict() for _ in range(200)],
                *[EsFilm.create_fake(genre=['Comedy']).dict() for _ in range(200)],
                *[EsFilm.create_fake(genre=['Action', 'Drama']).dict() for _ in range(30)],
                *[EsFilm.create_fake(genre=['Drama']).dict() for _ in range(11)]
            ],
            {'genre': 'Drama'},
            200,
            41,
            ResponseShortFilm,
            {},
        ),

        # Кейс получения первых 20 фильмов отсортированных по-возрастанию
        (
            [
                *[EsFilm.create_fake(imdb_rating=15).dict() for _ in range(5)],
                *[EsFilm.create_fake(imdb_rating=12.2).dict() for _ in range(150)],
                *[EsFilm.create_fake(imdb_rating=8).dict() for _ in range(20)],
                *[EsFilm.create_fake(imdb_rating=55.5).dict() for _ in range(150)],
                *[EsFilm.create_fake(imdb_rating=9.1).dict() for _ in range(6)],
            ],
            {'sort': 'imdb_rating', 'page_size': 20},
            200,
            20,
            ResponseShortFilm,
            {'imdb_rating': 8.0},
        ),

        # Кейс получения первых 20 фильмов отсортированных по-убыванию
        (
            [
                *[EsFilm.create_fake(imdb_rating=15).dict() for _ in range(5)],
                *[EsFilm.create_fake(imdb_rating=12.2).dict() for _ in range(150)],
                *[EsFilm.create_fake(imdb_rating=8).dict() for _ in range(20)],
                *[EsFilm.create_fake(imdb_rating=55.5).dict() for _ in range(150)],
                *[EsFilm.create_fake(imdb_rating=9.1).dict() for _ in range(6)],
            ],
            {'sort': '-imdb_rating', 'page_size': 20},
            200,
            20,
            ResponseShortFilm,
            {'imdb_rating': 55.5},
        ),

        # Кейс со всеми параметрами одновременно
        (
            [
                *[EsFilm.create_fake().dict() for _ in range(300)],
                *[EsFilm.create_fake(genre=['Drama']).dict() for _ in range(40)]
            ],
            {'sort': '-imdb_rating', 'page_size': 20, 'genre': 'Drama', 'page_number': 2},
            200,
            20,
            ResponseShortFilm,
            {},
        ),

        # Кейс с отсутствием фильмов по фильтрам
        (
            [
                *[EsFilm.create_fake(genre=['Action']).dict() for _ in range(300)],
                *[EsFilm.create_fake(genre=['Drama']).dict() for _ in range(40)]
            ],
            {'genre': 'Comedy'},
            200,
            0,
            ResponseShortFilm,
            {},
        ),
    ]
)
@pytest.mark.asyncio
async def test_get_films(
        redis_client,
        es_write_data: Callable,
        service_get_data: Callable,
        es_data: list[dict],  # данные для отправки в ES
        url_params: dict,  # параметры запроса
        res_status: int,  # код ответа
        res_count: str,  # количество элементов в ответе
        res_model: ModelMetaclass,  # модель ответа
        check_model_attrs: dict  # условия для сравнения атрибутов модели, например {'imdb_rating': '10'}
):
    """Тест: /api/v1/films
    """
    await es_write_data(es_data, 'movies')

    res = await service_get_data('films/', url_params)

    assert res.status == res_status
    assert len(res.body) == res_count
    for el in res.body:
        assert res_model.parse_obj(el)
        for attr, val in check_model_attrs.items():
            assert getattr(res_model.parse_obj(el), attr) == val


@pytest.mark.parametrize(
    'es_data, url_params, res_status, res_count, res_model, change_attrs',
    [
        # Кейс: ошибка валидации поля uuid
        (
            [EsFilm.create_fake().dict() for _ in range(200)],
            None,
            200,
            50,
            ResponseShortFilm,
            {'uuid': 123456},
        ),

        # Кейс: ошибка валидации поля title
        (
            [EsFilm.create_fake().dict() for _ in range(200)],
            None,
            200,
            50,
            ResponseShortFilm,
            {'title': []},
        ),

        # Кейс: ошибка валидации поля imdb_rating
        (
            [EsFilm.create_fake().dict() for _ in range(200)],
            None,
            200,
            50,
            ResponseShortFilm,
            {'imdb_rating': 'good'},
        ),
    ]
)
@pytest.mark.asyncio
async def test_get_films_no_valid(
        redis_client,
        es_write_data: Callable,
        service_get_data: Callable,
        es_data: list[dict],  # данные для отправки в ES
        url_params: dict,  # параметры запроса
        res_status: int,  # код ответа
        res_count: str,  # количество элементов в ответе
        res_model: ModelMetaclass,  # модель ответа
        change_attrs: dict  # подмена атрибута ответа, например {'imdb_rating': []}
):
    """Тест: /api/v1/films
    """
    await es_write_data(es_data, 'movies')

    res = await service_get_data('films/', url_params)

    assert res.status == res_status
    assert len(res.body) == res_count

    res.body[0].update(change_attrs)
    with pytest.raises(ValidationError):
        res_model.parse_obj(res.body[0])


@pytest.mark.parametrize(
    'es_data, url_params, res_status, res_count, res_model, check_model_attrs',
    [
        # Кейс получения всех фильмов использование кеша
        (
            [
                *[EsFilm.create_fake(imdb_rating=15).dict() for _ in range(200)],
                *[EsFilm.create_fake(imdb_rating=99).dict() for _ in range(20)],
            ],
            {'sort': '-imdb_rating', 'page_size': 20, 'page_number': 2},
            200,
            20,
            ResponseShortFilm,
            {'imdb_rating': 15.0},
        ),
    ]
)
@pytest.mark.asyncio
async def test_get_films_with_cache(
        redis_client,
        es_write_data: Callable,
        service_get_data: Callable,
        es_data: list[dict],  # данные для отправки в ES
        url_params: dict,  # параметры запроса
        res_status: int,  # код ответа
        res_count: str,  # количество элементов в ответе
        res_model: ModelMetaclass,  # модель ответа
        check_model_attrs: dict  # условия для сравнения атрибутов модели, например {'imdb_rating': '10'}
):
    """Тест: /api/v1/films
    """
    await es_write_data(es_data, 'movies')
    res1 = await service_get_data('films/', url_params)
    assert res1.status == res_status
    assert len(res1.body) == res_count
    for el in res1.body:
        assert res_model.parse_obj(el)
        for attr, val in check_model_attrs.items():
            assert getattr(res_model.parse_obj(el), attr) == val

    # Загружаем еще 20 фильмов - теперь на 2 странице рейтинг уже не 15,
    # но данные берутся из кеша, поэтому ничего не поменялось
    await es_write_data([EsFilm.create_fake(imdb_rating=99).dict() for _ in range(20)], 'movies')
    res2 = await service_get_data('films/', url_params)
    assert res1 == res2

    # Если же кеш сбросить и снова сделать тот же запрос,
    # ответ будет уже другой
    await redis_client.flushall()
    res3 = await service_get_data('films/', url_params)
    assert res1 != res3

    # и рейтинг фильмов уже не 15
    for el in res3.body:
        for attr, val in check_model_attrs.items():
            assert getattr(res_model.parse_obj(el), attr) == 99.0


@pytest.mark.parametrize(
    'es_data, id_, control_data, res_status, res_model, check_model_attrs',
    [
        # Кейс получения фильма по id
        (
            [
                *[EsFilm.create_fake().dict() for _ in range(200)],
                EsFilm.parse_obj(ES_FILMS_DATA).dict(),
            ],
            ES_FILMS_DATA['id'],
            ES_FILMS_DATA,
            200,
            ResponseFilm,
            {},
        ),

        # Кейс получения фильма по несуществующему id
        (
            [
                *[EsFilm.create_fake().dict() for _ in range(200)],
                EsFilm.parse_obj(ES_FILMS_DATA).dict(),
            ],
            '11111111-1111-1111-1111-111111111111',
            {},
            404,
            BaseModel,
            {},
        ),
    ]
)
@pytest.mark.asyncio
async def test_get_film_by_id(
        redis_client,
        es_write_data: Callable,
        service_get_data: Callable,
        es_data: list[dict],  # данные для отправки в ES
        id_: str,  # id запроса
        control_data: dict,  # фиксированные данные фильма
        res_status: int,  # код ответа
        res_model: ModelMetaclass,  # модель ответа
        check_model_attrs: dict  # условия для сравнения атрибутов модели, например {'imdb_rating': '10'}
):
    """Тест: /api/v1/films/<id>
    """
    await es_write_data(es_data, 'movies')

    control_film = res_model(
        uuid=control_data.get('id'),
        title=control_data.get('title'),
        imdb_rating=control_data.get('imdb_rating'),
        description=control_data.get('description'),
        genres=control_data.get('genre'),
        cast=[*control_data.get('actors_names', []), *control_data.get('writers_names', [])],
    )
    res = await service_get_data(f'films/{id_}')

    assert res.status == res_status
    assert res_model.parse_obj(res.body)
    res_film = res_model.parse_obj(res.body)
    assert res_film == control_film


@pytest.mark.parametrize(
    'es_data, res_status, res_model, change_attrs',
    [
        # Кейс: Невалидное значение title
        (
            [EsFilm.create_fake().dict() for _ in range(200)],
            200,
            ResponseFilm,
            {'title': None},
        ),

        # Кейс: Невалидное значение description
        (
            [EsFilm.create_fake().dict() for _ in range(200)],
            200,
            ResponseFilm,
            {'description': []},
        ),

        # Кейс: Невалидное значение imdb_rating
        (
                [EsFilm.create_fake().dict() for _ in range(200)],
                200,
                ResponseFilm,
                {'imdb_rating': None},
        ),

        # Кейс: Невалидное значение genres
        (
                [EsFilm.create_fake().dict() for _ in range(200)],
                200,
                ResponseFilm,
                {'genres': 'Comedy'},
        ),

        # Кейс: Невалидное значение cast
        (
                [EsFilm.create_fake().dict() for _ in range(200)],
                200,
                ResponseFilm,
                {'cast': 'Antony Boss'},
        ),


    ]
)
@pytest.mark.asyncio
async def test_get_film_by_id_not_valid(
        redis_client,
        es_write_data: Callable,
        service_get_data: Callable,
        es_data: list[dict],  # данные для отправки в ES
        res_status: int,  # код ответа
        res_model: ModelMetaclass,  # модель ответа
        change_attrs: dict  # подмена атрибута ответа, например {'imdb_rating': []}
):
    """Тест: /api/v1/films/<id>
    """
    await es_write_data(es_data, 'movies')

    films = await service_get_data('films/')
    res = await service_get_data(f"films/{films.body[0]['uuid']}")

    assert res.status == res_status

    res.body.update(change_attrs)
    with pytest.raises(ValidationError):
        res_model.parse_obj(res.body)
