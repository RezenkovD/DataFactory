from __future__ import annotations

import asyncio
from datetime import datetime
from decimal import Decimal
from pathlib import Path

import pandas as pd
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession

from ..core.config import settings
from ..db.base import Base
from ..db.session import get_engine, get_session
from ..models.credit import Credit
from ..models.dictionary import Dictionary
from ..models.payment import Payment
from ..models.plan import Plan
from ..models.user import User


async def seed_if_needed() -> None:
    if not settings.seed_on_startup:
        return

    engine = get_engine()
    await _ensure_db_ready(engine)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async for session in get_session():
        exists = await _has_any_users(session)
        if not exists:
            await _load_all(session)
        break


async def _ensure_db_ready(engine: AsyncEngine) -> None:
    max_attempts = 20
    delay_seconds = 1
    for attempt in range(1, max_attempts + 1):
        try:
            async with engine.connect() as conn:
                await conn.execute(text("SELECT 1"))
                return
        except (Exception,):
            if attempt == max_attempts:
                raise
            await asyncio.sleep(delay_seconds)


async def _has_any_users(session: AsyncSession) -> bool:
    result = await session.execute(text("SELECT 1 FROM users LIMIT 1"))
    return result.scalar() is not None


def _parse_date(value) -> datetime.date | None:
    if value is None:
        return None

    if isinstance(value, str) and value.strip() == "":
        return None

    try:
        if pd.isna(value):
            return None
    except (Exception,):
        pass

    for fmt in ("%Y-%m-%d", "%d.%m.%Y", "%Y/%m/%d"):
        try:
            return datetime.strptime(str(value), fmt).date()
        except (Exception,):
            continue

    ts = pd.to_datetime(value, errors="coerce")
    try:
        if pd.isna(ts):
            return None
    except (Exception,):
        pass
    return ts.date()


async def _load_all(session: AsyncSession) -> None:
    base = Path(__file__).resolve().parents[2] / "test_data"

    users_df = pd.read_csv(base / "users.csv", sep="\t")
    credits_df = pd.read_csv(base / "credits.csv", sep="\t")
    dictionary_df = pd.read_csv(base / "dictionary.csv", sep="\t")
    plans_df = pd.read_csv(base / "plans.csv", sep="\t")
    payments_df = pd.read_csv(base / "payments.csv", sep="\t")

    users = [
        User(
            id=int(r["id"]),
            login=str(r["login"]),
            registration_date=_parse_date(r["registration_date"]),
        )
        for _, r in users_df.iterrows()
    ]

    credits = [
        Credit(
            id=int(r["id"]),
            user_id=int(r["user_id"]),
            issuance_date=_parse_date(r["issuance_date"]),
            return_date=_parse_date(r.get("return_date")),
            actual_return_date=_parse_date(r.get("actual_return_date")),
            body=Decimal(r["body"]),
            percent=Decimal(r["percent"]),
        )
        for _, r in credits_df.iterrows()
    ]

    dictionary = [
        Dictionary(id=int(r["id"]), name=str(r["name"]))
        for _, r in dictionary_df.iterrows()
    ]

    plans = [
        Plan(
            id=int(r["id"]),
            period=_parse_date(r["period"]),
            sum=Decimal(r["sum"]),
            category_id=int(r["category_id"]),
        )
        for _, r in plans_df.iterrows()
    ]

    payments = [
        Payment(
            id=int(r["id"]),
            sum=Decimal(r["sum"]),
            payment_date=_parse_date(r["payment_date"]),
            credit_id=int(r["credit_id"]),
            type_id=int(r["type_id"]),
        )
        for _, r in payments_df.iterrows()
    ]

    session.add_all(users)
    session.add_all(dictionary)
    session.add_all(credits)
    session.add_all(plans)
    session.add_all(payments)
    await session.commit()
