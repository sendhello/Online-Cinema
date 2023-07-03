from .base import Model
from .mixins import IdMixin


class BaseRole(Model):
    title: str


class RoleInDB(BaseRole, IdMixin):
    """Модель роли в БД."""

    pass


class RoleCreate(BaseRole):
    pass


class RoleUpdate(BaseRole):
    """Модель роли для обновления данных."""

    pass


class RoleDelete(BaseRole):
    """Модель роли для удаления."""

    pass
