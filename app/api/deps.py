from __future__ import annotations

from typing import Any, AsyncGenerator

from fastapi import Depends, Header, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from ..core.config import settings
from ..db.session import get_session
from ..repositories.credit_repository import (
    CreditRepository,
    CreditRepositorySQLAlchemy,
)
from ..repositories.dictionary_repository import (
    DictionaryRepository,
    DictionaryRepositorySQLAlchemy,
)
from ..repositories.performance_repository import (
    PerformanceRepository,
    PerformanceRepositorySQLAlchemy,
)
from ..repositories.plans_repository import PlansRepository, PlansRepositorySQLAlchemy
from ..services.plan_import_service import PlansInsertService
from ..services.plan_performance_service import PlansService
from ..services.user_credits_service import UserCreditService
from ..services.year_performance_service import PerformanceService


async def get_db_session() -> AsyncGenerator[AsyncSession, Any]:
    async for s in get_session():
        yield s


async def require_api_key(x_api_key: str | None = Header(None)) -> None:
    if settings.api_key and x_api_key != settings.api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid API key"
        )


async def get_user_credit_service(
    session: AsyncSession = Depends(get_db_session),
) -> UserCreditService:
    repo: CreditRepository = CreditRepositorySQLAlchemy(session)
    return UserCreditService(repo)


async def get_performance_service(
    session: AsyncSession = Depends(get_db_session),
) -> PerformanceService:
    repo: PerformanceRepository = PerformanceRepositorySQLAlchemy(session)
    return PerformanceService(repo)


async def get_plans_service(
    session: AsyncSession = Depends(get_db_session),
) -> PlansService:
    plans_repo: PlansRepository = PlansRepositorySQLAlchemy(session)
    dict_repo: DictionaryRepository = DictionaryRepositorySQLAlchemy(session)
    performance_repo: PerformanceRepository = PerformanceRepositorySQLAlchemy(session)
    return PlansService(plans_repo, dict_repo, performance_repo)


async def get_plans_insert_service(
    session: AsyncSession = Depends(get_db_session),
) -> PlansInsertService:
    repo: PlansRepository = PlansRepositorySQLAlchemy(session)
    dict_repo: DictionaryRepository = DictionaryRepositorySQLAlchemy(session)
    return PlansInsertService(repo, dict_repo)
