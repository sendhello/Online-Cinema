from .base import Model
from .mixins import IdMixin
from .roles import RoleInDB
from constants import Service, Action, Resource


class Rule(Model):
    """Право доступа.
    """
    service: Service
    resource: Resource
    action: Action
