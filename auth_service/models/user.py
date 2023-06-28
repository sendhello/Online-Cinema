from db.postgres import Base, async_session
from sqlalchemy import Column, ForeignKey, String, select
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from werkzeug.security import check_password_hash, generate_password_hash

from .base_model import CRUDMixin, IDMixin


class User(Base, IDMixin, CRUDMixin):
    __tablename__ = 'users'

    login = Column(String(255), unique=True, nullable=False)
    password = Column(String(255), nullable=False)
    first_name = Column(String(50))
    last_name = Column(String(50))
    role_id = Column(UUID, ForeignKey('roles.id'))
    role = relationship('Role', back_populates='users')
    history = relationship('History', back_populates='user')

    def __init__(
        self, login: str, password: str, first_name: str, last_name: str
    ) -> None:
        self.login = login
        self.password = generate_password_hash(password)
        self.first_name = first_name
        self.last_name = last_name

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password, password)

    @classmethod
    async def get_by_login(cls, username: str) -> 'User':
        async with async_session() as session:
            request = select(cls).where(cls.login == username)
            result = await session.execute(request)
            user = result.scalars().first()

        return user

    def __repr__(self) -> str:
        return f'<User {self.login}>'
