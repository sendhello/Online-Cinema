import uuid
from datetime import datetime

from db.postgres import async_session
from sqlalchemy import Column, DateTime
from sqlalchemy.dialects.postgresql import UUID


class CRUDMixin:
    """Mixin-класс предоставляющий частые CRUD операции над моделями."""

    @classmethod
    async def create(cls, commit=True, **kwargs):
        instance = cls(**kwargs)
        return await instance._save(commit=commit)

    async def update(self, commit=True, **kwargs):
        for attr, value in kwargs.items():
            setattr(self, attr, value)

        return await self._save(commit=commit)

    async def delete(self, commit=True):
        async with async_session() as session:
            await session.delete(self)
            if commit:
                await session.commit()
                await session.refresh(self)

        return self

    async def _save(self, commit=True):
        async with async_session() as session:
            session.add(self)
            if commit:
                await session.commit()
                await session.refresh(self)

        return self


class IDMixin:
    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
        nullable=False,
    )
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.utcnow())
