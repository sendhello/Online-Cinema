from enum import Enum


ANONYMOUS = 'anonymous'


class Service(str, Enum):
    async_api = 'async_api'


class Resource(str, Enum):
    free_movie = 'free_movie'  # Фильмы для всех, не требуют регистрацию пользователей
    users_movie = 'users_movie'  # Фильмы для зарегистрированных пользователей
    subscription_movie = 'subscription_movie'  # Фильмы для пользователей с подпиской
    other = 'other'  # Фильмы для всех, не требуют регистрацию пользователей


class Action(str, Enum):
    create = 'create'
    read = 'read'
    update = 'update'
    delete = 'delete'