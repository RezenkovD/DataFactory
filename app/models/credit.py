from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import DECIMAL, BigInteger, Date, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..db.base import Base

if TYPE_CHECKING:
    from .payment import Payment
    from .user import User


class Credit(Base):
    __tablename__ = "credits"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    issuance_date: Mapped[date] = mapped_column(Date, nullable=False)
    return_date: Mapped[date] = mapped_column(Date, nullable=False)
    actual_return_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    body: Mapped[Decimal] = mapped_column(DECIMAL(16, 4), nullable=False)
    percent: Mapped[Decimal] = mapped_column(DECIMAL(16, 4), nullable=False)

    user: Mapped["User"] = relationship(back_populates="credits")
    payments: Mapped[list["Payment"]] = relationship(back_populates="credit")
