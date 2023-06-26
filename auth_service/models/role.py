from db.postgres import Base
from sqlalchemy import Column, String
from sqlalchemy.orm import relationship

from .base_model import IdMixin


class Role(Base, IdMixin):
    __tablename__ = "roles"

    title = Column(String(255), unique=True, nullable=False)
    users = relationship("User", back_populates="user")

    def __init__(self, title: str) -> None:
        self.title = title

    def __repr__(self) -> str:
        return f"<Role {self.title}>"
