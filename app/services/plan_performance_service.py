from __future__ import annotations

from calendar import monthrange
from datetime import date
from decimal import Decimal

from ..repositories.dictionary_repository import DictionaryRepository
from ..repositories.performance_repository import PerformanceRepository
from ..repositories.plans_repository import PlansRepository
from ..schemas.plan import PlanPerformanceItem, PlansPerformanceResponse
from . import COLLECTION_CATEGORY_ID, ISSUANCE_CATEGORY_ID


class PlansService:
    def __init__(
        self,
        plans_repo: PlansRepository,
        dict_repo: DictionaryRepository,
        performance_repo: PerformanceRepository,
    ) -> None:
        self.plans_repo = plans_repo
        self.dict_repo = dict_repo
        self.performance_repo = performance_repo

    async def get_plans_performance(self, as_of: date) -> PlansPerformanceResponse:
        year = as_of.year
        month = as_of.month
        start_date = date(year, month, 1)
        last_day_of_month = date(year, month, monthrange(year, month)[1])
        end_date = min(as_of, last_day_of_month)

        plans = await self.plans_repo.list_plans_for_month(year, month)
        names = await self.dict_repo.category_names()

        items: list[PlanPerformanceItem] = []
        issuances_actual_raw = await self.performance_repo.sum_issuances_until(
            start_date, end_date
        )
        payments_actual_raw = await self.performance_repo.sum_payments_until(
            start_date, end_date
        )

        issuances_actual = Decimal(str(issuances_actual_raw))
        payments_actual = Decimal(str(payments_actual_raw))

        for category_id, period, plan_sum in plans:
            plan_sum_dec = Decimal(str(plan_sum))
            if category_id == ISSUANCE_CATEGORY_ID:
                actual = issuances_actual
                category_name = names.get(category_id, "видача")
            elif category_id == COLLECTION_CATEGORY_ID:
                actual = payments_actual
                category_name = names.get(category_id, "збір")
            else:
                actual = Decimal("0")
                category_name = names.get(category_id, str(category_id))

            pct = (
                float((actual / plan_sum_dec) * Decimal("100"))
                if plan_sum_dec > Decimal("0")
                else 0.0
            )
            items.append(
                PlanPerformanceItem(
                    period=period,
                    category=category_name,
                    plan_sum=plan_sum_dec,
                    actual_sum=actual,
                    plan_percent=pct,
                )
            )

        return PlansPerformanceResponse(items=items)
