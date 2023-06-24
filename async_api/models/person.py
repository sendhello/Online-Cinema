from .base import Model, UUIDMixin


class Person(Model, UUIDMixin):
    full_name: str
