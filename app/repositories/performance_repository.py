from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import date

from sqlalchemy import extract, func, select

from ..models.credit import Credit
from ..models.payment import Payment
from ..models.plan import Plan
from .base import RepositorySQLAlchemy


class PerformanceRepository(ABC):
    @abstractmethod
    async def issuances_aggregates(
        self, year: int
    ) -> dict[tuple[int, int], tuple[int, float]]:
        raise NotImplementedError()

    @abstractmethod
    async def payments_aggregates(
        self, year: int
    ) -> dict[tuple[int, int], tuple[int, float]]:
        raise NotImplementedError()

    @abstractmethod
    async def plans_sum_by_category(
        self, year: int
    ) -> dict[tuple[int, int], dict[int, float]]:
        raise NotImplementedError()

    @abstractmethod
    async def sum_issuances_until(self, start_date: date, end_date: date) -> float:
        raise NotImplementedError()

    @abstractmethod
    async def sum_payments_until(self, start_date: date, end_date: date) -> float:
        raise NotImplementedError()


class PerformanceRepositorySQLAlchemy(RepositorySQLAlchemy, PerformanceRepository):
    async def issuances_aggregates(
        self, year: int
    ) -> dict[tuple[int, int], tuple[int, float]]:
        stmt = (
            select(
                extract("year", Credit.issuance_date).label("y"),
                extract("month", Credit.issuance_date).label("m"),
                func.count(Credit.id),
                func.coalesce(func.sum(Credit.body), 0.0),
            )
            .where(extract("year", Credit.issuance_date) == year)
            .group_by("y", "m")
        )
        res = await self._execute(stmt)
        data: dict[tuple[int, int], tuple[int, float]] = {}
        for y, m, cnt, summ in res.all():
            data[(int(y), int(m))] = (int(cnt), float(summ or 0.0))
        return data

    async def payments_aggregates(
        self, year: int
    ) -> dict[tuple[int, int], tuple[int, float]]:
        stmt = (
            select(
                extract("year", Payment.payment_date).label("y"),
                extract("month", Payment.payment_date).label("m"),
                func.count(Payment.id),
                func.coalesce(func.sum(Payment.sum), 0.0),
            )
            .where(extract("year", Payment.payment_date) == year)
            .group_by("y", "m")
        )
        res = await self._execute(stmt)
        data: dict[tuple[int, int], tuple[int, float]] = {}
        for y, m, cnt, summ in res.all():
            data[(int(y), int(m))] = (int(cnt), float(summ or 0.0))
        return data

    async def plans_sum_by_category(
        self, year: int
    ) -> dict[tuple[int, int], dict[int, float]]:
        stmt = (
            select(
                extract("year", Plan.period).label("y"),
                extract("month", Plan.period).label("m"),
                Plan.category_id,
                func.coalesce(func.sum(Plan.sum), 0.0),
            )
            .where(extract("year", Plan.period) == year)
            .group_by("y", "m", Plan.category_id)
        )
        res = await self._execute(stmt)
        data: dict[tuple[int, int], dict[int, float]] = {}
        for y, m, cat, summ in res.all():
            key = (int(y), int(m))
            bucket = data.setdefault(key, {})
            bucket[int(cat)] = float(summ or 0.0)
        return data

    async def sum_issuances_until(self, start_date: date, end_date: date) -> float:
        stmt = (
            select(func.coalesce(func.sum(Credit.body), 0.0))
            .where(Credit.issuance_date >= start_date)
            .where(Credit.issuance_date <= end_date)
        )
        res = await self._execute(stmt)
        return float(res.scalar() or 0.0)

    async def sum_payments_until(self, start_date: date, end_date: date) -> float:
        stmt = (
            select(func.coalesce(func.sum(Payment.sum), 0.0))
            .where(Payment.payment_date >= start_date)
            .where(Payment.payment_date <= end_date)
        )
        res = await self._execute(stmt)
        return float(res.scalar() or 0.0)
