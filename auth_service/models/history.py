from db.postgres import Base, async_session
from sqlalchemy import Column, ForeignKey, String, select
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from .mixins import CRUDMixin, IDMixin


class History(Base, IDMixin, CRUDMixin):
    __tablename__ = 'history'

    user_agent = Column(String(255), nullable=False)
    user_id = Column(UUID, ForeignKey('users.id'))
    user = relationship('User', back_populates='history')

    def __init__(self, user_id: UUID, user_agent: str) -> None:
        self.user_id = user_id
        self.user_agent = user_agent

    @classmethod
    async def get_by_user_id(cls, user_id: UUID) -> list['History']:
        async with async_session() as session:
            request = select(cls).where(cls.user_id == user_id)
            result = await session.execute(request)
            entities = result.scalars().all()

        return entities

    def __repr__(self) -> str:
        return f'<History element {self.user_agent}>'
