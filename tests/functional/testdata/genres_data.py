from functional.utils.models.genre import GenreData, GenresListData

GENRE_DATA = [
    GenreData(
        genre_id='11111111-1111-1111-1111-111111111111',
        es_data=[
            {
                'id': '11111111-1111-1111-1111-111111111111',
                'name': 'Fantastic',
            },
            {
                'id': '22222222-2222-2222-2222-222222222222',
                'name': 'Fantasy',
            },
        ],
        expected_data={
            'uuid': '11111111-1111-1111-1111-111111111111',
            'name': 'Fantastic',
        },
    ).dict().values(),
]

GENRES_LIST_DATA = [
    GenresListData(
        es_data=[
            {
                'id': '11111111-1111-1111-1111-111111111111',
                'name': 'Fantastic',
            },
            {
                'id': '22222222-2222-2222-2222-222222222222',
                'name': 'Fantasy',
            },
        ],
        expected_data=[
            {
                'uuid': '11111111-1111-1111-1111-111111111111',
                'name': 'Fantastic',
            },
            {
                'uuid': '22222222-2222-2222-2222-222222222222',
                'name': 'Fantasy',
            },
        ],

    ).dict().values(),
]
