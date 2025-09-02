from __future__ import annotations

from datetime import date
from typing import TYPE_CHECKING

from sqlalchemy import BigInteger, Date, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..db.base import Base

if TYPE_CHECKING:
    from .credit import Credit


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    login: Mapped[str] = mapped_column(String(256), unique=True, nullable=False)
    registration_date: Mapped[date] = mapped_column(Date, nullable=False)

    credits: Mapped[list["Credit"]] = relationship(back_populates="user")
