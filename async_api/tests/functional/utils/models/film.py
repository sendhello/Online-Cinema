from faker import Faker

from . import EsModel, ResponseModel

fake = Faker()

GENRES = [
    'Action',
    'Adventure',
    'Fantasy',
    'Sci-Fi',
    'Drama',
    'Music',
    'Romance',
    'Thriller',
    'Mystery',
    'Comedy',
]


class EsPerson(EsModel):
    name: str

    @classmethod
    def create_fake(cls, **kwargs):
        return cls(
            id=kwargs.get('id', fake.uuid4()),
            name=kwargs.get('name', fake.name()),
        )


class EsFilm(EsModel):
    title: str
    description: str
    imdb_rating: float
    actors: list[EsPerson]
    writers: list[EsPerson]
    actors_names: list[str]
    director: list[str]
    writers_names: list[str]
    genre: list[str]

    @classmethod
    def create_fake(cls, **kwargs):
        actors = [EsPerson.create_fake(**kwargs) for _ in range(fake.pyint(min_value=1, max_value=10))]
        writers = [EsPerson.create_fake(**kwargs) for _ in range(fake.pyint(min_value=1, max_value=10))]
        return cls(
            id=kwargs.get('id', fake.uuid4()),
            title=kwargs.get('title', fake.catch_phrase()),
            description=kwargs.get('description', fake.paragraph(nb_sentences=3)),
            imdb_rating=kwargs.get('imdb_rating', round(fake.pyfloat(min_value=0, max_value=100), 1)),
            actors=kwargs.get('actors', actors),
            writers=kwargs.get('writers', writers),
            actors_names=kwargs.get('actors_names', [actor.name for actor in actors]),
            director=kwargs.get('director', [fake.name() for _ in range(fake.pyint(min_value=1, max_value=3))]),
            writers_names=kwargs.get('writers_names', [writer.name for writer in writers]),
            genre=kwargs.get(
                'genre',
                fake.random_elements(elements=GENRES, length=fake.pyint(min_value=1, max_value=3), unique=True)
            )
        )


class ResponseShortFilm(ResponseModel):
    """Модель фильма из списка фильмов.
    """
    title: str
    imdb_rating: float


class ResponseFilm(ResponseModel):
    """Модель фильма со страницы фильма
    """
    title: str
    imdb_rating: float
    description: str | None
    genres: list[str] = []
    cast: list[str] = []
