from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Sequence, Type

from sqlalchemy import select
from sqlalchemy.orm import selectinload

from ..models.credit import Credit
from .base import CRUDRepository, CRUDRepositorySQLAlchemy, T


class CreditRepository(CRUDRepository[Credit, int], ABC):
    @abstractmethod
    async def list_by_user(self, user_id: int) -> Sequence[Credit]:
        raise NotImplementedError()


class CreditRepositorySQLAlchemy(
    CreditRepository, CRUDRepositorySQLAlchemy[Credit, int]
):
    async def list_by_user(self, user_id: int) -> Sequence[Credit]:
        stmt = (
            select(Credit)
            .where(Credit.user_id == user_id)
            .options(selectinload(Credit.payments))
        )
        result = await self._execute(stmt)
        credits = list(result.scalars().unique().all())
        return credits

    @property
    def get_entity_class(self) -> Type[T]:
        return Credit
