from __future__ import annotations

from datetime import date
from decimal import Decimal

from . import BaseSchema


class ClosedCreditInfo(BaseSchema):
    return_date: date
    body: Decimal
    percent: Decimal
    total_payments_sum: Decimal


class OpenCreditInfo(BaseSchema):
    due_date: date
    overdue_days: int
    body: Decimal
    percent: Decimal
    principal_payments_sum: Decimal
    interest_payments_sum: Decimal


class CreditItem(BaseSchema):
    issuance_date: date
    is_closed: bool
    closed: ClosedCreditInfo | None = None
    open: OpenCreditInfo | None = None


class CreditListResponse(BaseSchema):
    items: list[CreditItem]
