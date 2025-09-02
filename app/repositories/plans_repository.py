from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import date
from typing import Type

from sqlalchemy import and_, extract, select

from ..models.plan import Plan
from .base import CRUDRepository, CRUDRepositorySQLAlchemy, T


class PlansRepository(CRUDRepository[Plan, int], ABC):
    @abstractmethod
    async def list_plans_for_month(
        self, year: int, month: int
    ) -> list[tuple[int, date, float]]:
        raise NotImplementedError()

    @abstractmethod
    async def exists_plan(self, period: date, category_id: int) -> bool:
        raise NotImplementedError()


class PlansRepositorySQLAlchemy(PlansRepository, CRUDRepositorySQLAlchemy[Plan, int]):
    async def list_plans_for_month(
        self, year: int, month: int
    ) -> list[tuple[int, date, float]]:
        stmt = (
            select(Plan.category_id, Plan.period, Plan.sum)
            .where(extract("year", Plan.period) == year)
            .where(extract("month", Plan.period) == month)
        )
        res = await self._execute(stmt)
        return [(int(cid), per, float(s)) for cid, per, s in res.all()]

    async def exists_plan(self, period: date, category_id: int) -> bool:
        stmt = (
            select(Plan.id)
            .where(and_(Plan.period == period, Plan.category_id == category_id))
            .limit(1)
        )
        res = await self._execute(stmt)
        return res.scalar() is not None

    @property
    def get_entity_class(self) -> Type[T]:
        return Plan
