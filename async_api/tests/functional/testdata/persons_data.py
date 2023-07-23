from ..utils.models.person import (
    PersonData,
    PersonFilmsData,
    PersonsData,
    PersonSearchData,
)


PERSONS_DATA = [
    PersonsData(
        es_data=[
            {
                'id': '11111111-1111-1111-1111-111111111111',
                'full_name': 'George Dzikovitskey',
            },
            {
                'id': '22222222-2222-2222-2222-222222222222',
                'full_name': 'George Kundashvilli',
            },
        ],
        expected_data=[
            {
                'uuid': '11111111-1111-1111-1111-111111111111',
                'full_name': 'George Dzikovitskey',
            },
            {
                'uuid': '22222222-2222-2222-2222-222222222222',
                'full_name': 'George Kundashvilli',
            },
        ],
    )
    .dict()
    .values(),
]

PERSON_BY_UUID_DATA = [
    PersonData(
        person_uuid='11111111-1111-1111-1111-111111111111',
        es_data=[
            {
                'id': '11111111-1111-1111-1111-111111111111',
                'full_name': 'George Dzikovitskey',
            },
            {
                'id': '22222222-2222-2222-2222-222222222222',
                'full_name': 'George Kundashvilli',
            },
        ],
        expected_data={
            'uuid': '11111111-1111-1111-1111-111111111111',
            'full_name': 'George Dzikovitskey',
            'films': [],
        },
    )
    .dict()
    .values(),
]

PERSON_FILMS_BY_UUID_DATA = [
    PersonFilmsData(
        person_uuid='11111111-1111-1111-1111-111111111111',
        es_data={
            'persons': [
                {
                    'id': '11111111-1111-1111-1111-111111111111',
                    'full_name': 'George Dzikovitskey',
                },
            ],
            'movies': [
                {
                    "id": '22222222-2222-2222-2222-222222222222',
                    "imdb_rating": 8.1,
                    "genre": ['Comedy'],
                    "title": 'Super movie',
                    "description": 'About tests',
                    "director": [],
                    "actors_names": ['George Dzikovitskey'],
                    "writers_names": [],
                    "actors": [
                        {
                            'id': '11111111-1111-1111-1111-111111111111',
                            'name': 'George Dzikovitskey',
                        },
                    ],
                    "writers": [],
                },
            ],
        },
        expected_data=[
            {
                'uuid': '22222222-2222-2222-2222-222222222222',
                'title': 'Super movie',
                'imdb_rating': 8.1,
            },
        ],
    )
    .dict()
    .values(),
]
PERSON_SEARCH_DATA = [
    PersonSearchData(
        params='?page_size=50&page_number=1&query=George',
        es_data={
            'persons': [
                {
                    'id': '11111111-1111-1111-1111-111111111111',
                    'full_name': 'George Dzikovitskey',
                },
                {
                    'id': '22222222-2222-2222-2222-222222222222',
                    'full_name': 'George Kundashvilli',
                },
            ],
            'movies': [
                {
                    "id": '22222222-2222-2222-2222-222222222222',
                    "imdb_rating": 8.1,
                    "genre": ['Comedy'],
                    "title": 'Super movie',
                    "description": 'About tests',
                    "director": [],
                    "actors_names": ['George Dzikovitskey'],
                    "writers_names": [],
                    "actors": [
                        {
                            'id': '11111111-1111-1111-1111-111111111111',
                            'name': 'George Dzikovitskey',
                        },
                    ],
                    "writers": [],
                },
                {
                    "id": '11111111-1111-1111-1111-111111111111',
                    "imdb_rating": 8.1,
                    "genre": ['Comedy'],
                    "title": 'Bad movie',
                    "description": 'Not about tests',
                    "director": [],
                    "actors_names": ['George Dzikovitskey', 'George Kundashvilli'],
                    "writers_names": [],
                    "actors": [
                        {
                            'id': '11111111-1111-1111-1111-111111111111',
                            'name': 'George Dzikovitskey',
                        },
                        {
                            'id': '22222222-2222-2222-2222-222222222222',
                            'name': 'Vasya Kundashvilli',
                        },
                    ],
                    "writers": [],
                },
            ],
        },
        expected_data=[
            {
                'uuid': '11111111-1111-1111-1111-111111111111',
                'full_name': 'George Dzikovitskey',
                'films': [
                    {
                        'uuid': '22222222-2222-2222-2222-222222222222',
                        'roles': ['actors'],
                    },
                    {
                        'uuid': '11111111-1111-1111-1111-111111111111',
                        'roles': ['actors'],
                    },
                ],
            },
            {
                'uuid': '22222222-2222-2222-2222-222222222222',
                'full_name': 'George Kundashvilli',
                'films': [
                    {
                        'uuid': '11111111-1111-1111-1111-111111111111',
                        'roles': ['actors'],
                    },
                ],
            },
        ],
    )
    .dict()
    .values(),
]
