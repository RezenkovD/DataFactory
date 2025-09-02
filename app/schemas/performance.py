from __future__ import annotations

from decimal import Decimal

from . import BaseSchema


class YearPerformanceItem(BaseSchema):
    month: int
    year: int
    issuances_count: int
    issuances_plan_sum: Decimal
    issuances_sum: Decimal
    issuances_plan_percent: float
    payments_count: int
    collections_plan_sum: Decimal
    payments_sum: Decimal
    collections_plan_percent: float
    issuances_share_of_year_percent: float
    payments_share_of_year_percent: float


class YearPerformanceResponse(BaseSchema):
    items: list[YearPerformanceItem]
