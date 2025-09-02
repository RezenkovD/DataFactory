from __future__ import annotations

from datetime import date
from decimal import Decimal

from . import BaseSchema


class PlanPerformanceItem(BaseSchema):
    period: date
    category: str
    plan_sum: Decimal
    actual_sum: Decimal
    plan_percent: float


class PlansPerformanceResponse(BaseSchema):
    items: list[PlanPerformanceItem]


class PlansInsertResponse(BaseSchema):
    message: str
