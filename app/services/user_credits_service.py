from __future__ import annotations

from datetime import date
from decimal import Decimal

from ..repositories.credit_repository import CreditRepository
from ..schemas.credit import (
    ClosedCreditInfo,
    CreditItem,
    CreditListResponse,
    OpenCreditInfo,
)


class UserCreditService:
    def __init__(self, credit_repo: CreditRepository) -> None:
        self.credit_repo = credit_repo

    async def get_user_credits(self, user_id: int) -> CreditListResponse:
        credits = await self.credit_repo.list_by_user(user_id)
        items: list[CreditItem] = []
        for c in credits:
            is_closed = c.actual_return_date is not None
            issuance_date = c.issuance_date
            body = Decimal(str(c.body))
            percent = Decimal(str(c.percent))
            if is_closed:
                total_payments = sum(
                    (Decimal(str(p.sum)) for p in c.payments), Decimal("0")
                )
                closed_info = ClosedCreditInfo(
                    return_date=c.actual_return_date,
                    body=body,
                    percent=percent,
                    total_payments_sum=total_payments,
                )
                items.append(
                    CreditItem(
                        issuance_date=issuance_date,
                        is_closed=True,
                        closed=closed_info,
                    )
                )
            else:
                today = date.today()
                due_date = c.return_date
                overdue_days = max(0, (today - due_date).days) if due_date else 0
                principal_payments = sum(
                    (Decimal(str(p.sum)) for p in c.payments if p.type_id == 1),
                    Decimal("0"),
                )
                interest_payments = sum(
                    (Decimal(str(p.sum)) for p in c.payments if p.type_id == 2),
                    Decimal("0"),
                )
                open_info = OpenCreditInfo(
                    due_date=due_date,
                    overdue_days=overdue_days,
                    body=body,
                    percent=percent,
                    principal_payments_sum=principal_payments,
                    interest_payments_sum=interest_payments,
                )
                items.append(
                    CreditItem(
                        issuance_date=issuance_date,
                        is_closed=False,
                        open=open_info,
                    )
                )
        return CreditListResponse(items=items)
