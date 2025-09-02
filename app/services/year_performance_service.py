from __future__ import annotations

from decimal import Decimal

from ..repositories.performance_repository import PerformanceRepository
from ..schemas.performance import YearPerformanceItem, YearPerformanceResponse
from . import COLLECTION_CATEGORY_ID, ISSUANCE_CATEGORY_ID


class PerformanceService:
    def __init__(self, repo: PerformanceRepository) -> None:
        self.repo = repo

    async def get_year_performance(self, year: int) -> YearPerformanceResponse:
        issuances = await self.repo.issuances_aggregates(year)
        payments = await self.repo.payments_aggregates(year)
        plans = await self.repo.plans_sum_by_category(year)

        total_issuances_sum: Decimal = sum(
            (Decimal(str(v[1])) for v in issuances.values()), Decimal("0")
        )
        total_payments_sum: Decimal = sum(
            (Decimal(str(v[1])) for v in payments.values()), Decimal("0")
        )

        items: list[YearPerformanceItem] = []
        for month in range(1, 12 + 1):
            key = (year, month)
            iss_cnt, iss_sum_raw = issuances.get(key, (0, 0.0))
            pay_cnt, pay_sum_raw = payments.get(key, (0, 0.0))
            plan_bucket = plans.get(key, {})
            iss_plan_raw = plan_bucket.get(ISSUANCE_CATEGORY_ID, 0.0)
            coll_plan_raw = plan_bucket.get(COLLECTION_CATEGORY_ID, 0.0)

            iss_sum = Decimal(str(iss_sum_raw))
            pay_sum = Decimal(str(pay_sum_raw))
            iss_plan = Decimal(str(iss_plan_raw))
            coll_plan = Decimal(str(coll_plan_raw))

            iss_plan_pct = (
                float((iss_sum / iss_plan) * Decimal("100"))
                if iss_plan > Decimal("0")
                else 0.0
            )
            coll_plan_pct = (
                float((pay_sum / coll_plan) * Decimal("100"))
                if coll_plan > Decimal("0")
                else 0.0
            )
            iss_share_year = (
                float((iss_sum / total_issuances_sum) * Decimal("100"))
                if total_issuances_sum > Decimal("0")
                else 0.0
            )
            pay_share_year = (
                float((pay_sum / total_payments_sum) * Decimal("100"))
                if total_payments_sum > Decimal("0")
                else 0.0
            )

            items.append(
                YearPerformanceItem(
                    month=month,
                    year=year,
                    issuances_count=iss_cnt,
                    issuances_plan_sum=iss_plan,
                    issuances_sum=iss_sum,
                    issuances_plan_percent=iss_plan_pct,
                    payments_count=pay_cnt,
                    collections_plan_sum=coll_plan,
                    payments_sum=pay_sum,
                    collections_plan_percent=coll_plan_pct,
                    issuances_share_of_year_percent=iss_share_year,
                    payments_share_of_year_percent=pay_share_year,
                )
            )

        return YearPerformanceResponse(items=items)
