from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from typing import Dict, Iterable, List, Set, Tuple

import pandas as pd

from ..exceptions import ValidationException
from ..models.plan import Plan
from ..repositories.dictionary_repository import DictionaryRepository
from ..repositories.plans_repository import PlansRepository

PLAN_MONTH_COL: str = "місяць плану"
CATEGORY_NAME_COL: str = "назва категорії плану"
SUM_COL: str = "сума"

ALLOWED_CATEGORY_NAMES: Set[str] = {"видача", "збір"}

RowIndex = int
CategoryId = int
NormalizedCategoryName = str
PlanRow = Tuple[date, CategoryId, float, RowIndex]


class PlansInsertService:
    def __init__(self, repo: PlansRepository, dict_repo: DictionaryRepository) -> None:
        self.repo = repo
        self.dict_repo = dict_repo

    async def insert_from_excel(self, file_path: str) -> str:
        df = self._read_excel(file_path)

        column_mapping = self._build_column_mapping(df.columns)
        normalized_name_to_id = await self._build_category_map()
        self._ensure_required_categories_present(normalized_name_to_id)

        rows = self._extract_rows(df, column_mapping, normalized_name_to_id)
        self._ensure_no_duplicate_rows(rows)

        existing_pairs = await self._load_existing_pairs(rows)
        self._ensure_no_conflicts_with_existing(
            rows, normalized_name_to_id, existing_pairs
        )

        entities = self._build_entities(rows)
        if entities:
            await self.repo.update_many(entities)

        return f"Inserted {len(rows)} plan row(s)"

    async def _build_category_map(self) -> Dict[NormalizedCategoryName, CategoryId]:
        category_names = {
            k: v for k, v in (await self.dict_repo.category_names()).items()
        }
        return {
            str(name).strip().lower(): int(cid) for cid, name in category_names.items()
        }

    def _extract_rows(
        self,
        df: pd.DataFrame,
        mapping: Dict[str, str],
        name_to_id: Dict[NormalizedCategoryName, CategoryId],
    ) -> List[PlanRow]:
        rows: List[PlanRow] = []
        for idx, record in df.iterrows():
            row_num = idx + 2
            period_raw = record[mapping[PLAN_MONTH_COL]]
            category_name = str(record[mapping[CATEGORY_NAME_COL]]).strip().lower()
            sum_value_raw = record[mapping[SUM_COL]]

            try:
                sum_value = self._parse_sum(sum_value_raw)
            except ValidationException as err:
                raise ValidationException(f"Row {row_num}: {err}")

            period = self._parse_period(period_raw, row_num)

            if category_name not in ALLOWED_CATEGORY_NAMES:
                raise ValidationException(
                    f"Row {row_num}: unknown category '{category_name}'"
                )

            category_id = name_to_id[category_name]
            rows.append((period, category_id, sum_value, idx))

        return rows

    async def _load_existing_pairs(
        self, rows: List[PlanRow]
    ) -> Set[Tuple[date, CategoryId]]:
        unique_months: Set[Tuple[int, int]] = {
            (p.year, p.month) for p, _c, _s, _i in rows
        }
        existing_pairs: Set[Tuple[date, CategoryId]] = set()
        for year, month in sorted(unique_months):
            for cid, per, _s in await self.repo.list_plans_for_month(year, month):
                existing_pairs.add((per, cid))
        return existing_pairs

    @staticmethod
    def _read_excel(file_path: str) -> pd.DataFrame:
        try:
            return pd.read_excel(file_path)
        except Exception as exc:
            raise ValidationException(f"Failed to read Excel: {exc}")

    @staticmethod
    def _build_column_mapping(columns: Iterable[str]) -> Dict[str, str]:
        required_cols = {PLAN_MONTH_COL, CATEGORY_NAME_COL, SUM_COL}
        mapping: Dict[str, str] = {}
        for col in required_cols:
            matches = [c for c in columns if c.strip().lower() == col]
            if not matches:
                raise ValidationException(f"Missing required column: {col}")
            mapping[col] = matches[0]
        return mapping

    @staticmethod
    def _ensure_required_categories_present(
        name_to_id: Dict[NormalizedCategoryName, CategoryId],
    ) -> None:
        for required_name in ALLOWED_CATEGORY_NAMES:
            if required_name not in name_to_id:
                raise ValidationException(
                    f"Dictionary is missing required category '{required_name}'"
                )

    @staticmethod
    def _parse_sum(value) -> float:
        if pd.isna(value):
            raise ValidationException("Column 'сума' contains empty value(s)")
        if isinstance(value, (int, float)):
            return float(value)
        try:
            text = str(value).strip().replace("\u00a0", " ")
            text = text.replace(" ", "")
            if "," in text and "." not in text:
                text = text.replace(",", ".")
            return float(text)
        except Exception:
            raise ValidationException("Column 'сума' contains non-numeric value(s)")

    @staticmethod
    def _parse_period(value, row_num: int) -> date:
        try:
            if isinstance(value, (datetime, date)):
                parsed = date(value.year, value.month, value.day)
            else:
                parsed = pd.to_datetime(value).date()
        except Exception:
            raise ValidationException(f"Row {row_num}: invalid '{PLAN_MONTH_COL}'")
        if parsed.day != 1:
            raise ValidationException(
                f"Row {row_num}: '{PLAN_MONTH_COL}' must be the first day of month"
            )
        return parsed

    @staticmethod
    def _ensure_no_duplicate_rows(rows: List[PlanRow]) -> None:
        seen: Dict[Tuple[date, CategoryId], RowIndex] = {}
        for period, category_id, _sum, idx in rows:
            key = (period, category_id)
            if key in seen:
                first_row_num = seen[key] + 2
                raise ValidationException(
                    f"Row {idx+2}: duplicate plan for {period.isoformat()} and category already present in row {first_row_num}"
                )
            seen[key] = idx

    @staticmethod
    def _ensure_no_conflicts_with_existing(
        rows: List[PlanRow],
        name_to_id: Dict[NormalizedCategoryName, CategoryId],
        existing_pairs: Set[Tuple[date, CategoryId]],
    ) -> None:
        if not rows:
            return
        inv_map = {v: k for k, v in name_to_id.items()}
        for period, category_id, _sum, idx in rows:
            if (period, category_id) in existing_pairs:
                category_name = inv_map.get(category_id, str(category_id))
                raise ValidationException(
                    f"Row {idx+2}: plan for {period.isoformat()} and category {category_name} already exists"
                )

    @staticmethod
    def _build_entities(rows: List[PlanRow]) -> List[Plan]:
        return [
            Plan(period=period, category_id=category_id, sum=Decimal(sum_value))
            for period, category_id, sum_value, _idx in rows
        ]
