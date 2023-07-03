from db.postgres import Base
from sqlalchemy import Column, String
from sqlalchemy.orm import relationship

from .mixins import CRUDMixin, IDMixin


class Role(Base, IDMixin, CRUDMixin):
    __tablename__ = 'roles'

    title = Column(String(255), unique=True, nullable=False)
    users = relationship('User', back_populates='role')

    def __init__(self, title: str) -> None:
        self.title = title

    def __repr__(self) -> str:
        return f'<Role {self.title}>'
