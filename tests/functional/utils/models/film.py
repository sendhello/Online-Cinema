from functional.utils.models.base_models import IDMixin


class PersonName(IDMixin):
    name: str


class Film(IDMixin):
    """Модель фильма из БД.
    """
    title: str
    imdb_rating: float
    description: str | None
    genre: list[str] = []
    actors: list[PersonName] = []
    writers: list[PersonName] = []
    director: list[PersonName] = []
    actors_names: list[str] = []
    writers_names: list[str] = []

