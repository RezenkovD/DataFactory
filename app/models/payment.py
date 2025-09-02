from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import DECIMAL, BigInteger, Date, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..db.base import Base

if TYPE_CHECKING:
    from .credit import Credit


class Payment(Base):
    __tablename__ = "payments"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    sum: Mapped[Decimal] = mapped_column(DECIMAL(16, 4), nullable=False)
    payment_date: Mapped[date] = mapped_column(Date, nullable=False)
    credit_id: Mapped[int] = mapped_column(
        ForeignKey("credits.id", ondelete="CASCADE"), index=True
    )
    type_id: Mapped[int] = mapped_column(ForeignKey("dictionary.id"), nullable=False)

    credit: Mapped["Credit"] = relationship(back_populates="payments")
