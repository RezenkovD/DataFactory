from __future__ import annotations

import tempfile
from datetime import date

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile

from ..api.deps import (
    get_performance_service,
    get_plans_insert_service,
    get_plans_service,
    get_user_credit_service,
    require_api_key,
)
from ..schemas.credit import CreditListResponse
from ..schemas.performance import YearPerformanceResponse
from ..schemas.plan import PlansInsertResponse, PlansPerformanceResponse
from ..services.plan_import_service import PlansInsertService
from ..services.plan_performance_service import PlansService
from ..services.user_credits_service import UserCreditService
from ..services.year_performance_service import PerformanceService

api_router = APIRouter(prefix="/api", dependencies=[Depends(require_api_key)])


@api_router.get("/user_credits/{user_id}", response_model=CreditListResponse)
async def user_credits(
    user_id: int, service: UserCreditService = Depends(get_user_credit_service)
) -> CreditListResponse:
    return await service.get_user_credits(user_id)


@api_router.get("/year_performance/{year}", response_model=YearPerformanceResponse)
async def year_performance(
    year: int, service: PerformanceService = Depends(get_performance_service)
) -> YearPerformanceResponse:
    return await service.get_year_performance(year)


@api_router.get("/plans_performance", response_model=PlansPerformanceResponse)
async def plans_performance(
    date_str: date = Query(..., alias="date"),
    service: PlansService = Depends(get_plans_service),
) -> PlansPerformanceResponse:
    return await service.get_plans_performance(date_str)


@api_router.post("/plans_insert", response_model=PlansInsertResponse)
async def plans_insert(
    file: UploadFile = File(
        ...,
        description="Excel file with columns: місяць плану, назва категорії плану, сума",
    ),
    service: PlansInsertService = Depends(get_plans_insert_service),
) -> PlansInsertResponse:
    suffix = ".xlsx" if not file.filename.endswith((".xls", ".xlsx")) else None
    with tempfile.NamedTemporaryFile(delete=True, suffix=suffix) as tmp:
        content = await file.read()
        tmp.write(content)
        tmp.flush()
        try:
            message = await service.insert_from_excel(tmp.name)
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))
    return PlansInsertResponse(message=message)
