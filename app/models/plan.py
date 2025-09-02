from __future__ import annotations

from datetime import date
from decimal import Decimal

from sqlalchemy import DECIMAL, BigInteger, Date, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from ..db.base import Base


class Plan(Base):
    __tablename__ = "plans"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    period: Mapped[date] = mapped_column(Date, nullable=False)
    sum: Mapped[Decimal] = mapped_column(DECIMAL(16, 4), nullable=False)
    category_id: Mapped[int] = mapped_column(
        ForeignKey("dictionary.id"), nullable=False
    )
