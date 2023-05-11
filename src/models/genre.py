from . import Model, UUIDMixin


class Genre(Model, UUIDMixin):
    name: str
