from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Type

from sqlalchemy import select

from ..models.dictionary import Dictionary
from .base import CRUDRepositorySQLAlchemy, T


class DictionaryRepository(ABC):
    @abstractmethod
    async def category_names(self) -> dict[int, str]:
        raise NotImplementedError()

    @abstractmethod
    async def category_id_by_name(self, name: str) -> int | None:
        raise NotImplementedError()


class DictionaryRepositorySQLAlchemy(
    DictionaryRepository, CRUDRepositorySQLAlchemy[Dictionary, int]
):
    async def category_names(self) -> dict[int, str]:
        res = await self._execute(select(Dictionary.id, Dictionary.name))
        return {int(i): str(n) for i, n in res.all()}

    async def category_id_by_name(self, name: str) -> int | None:
        stmt = select(Dictionary.id).where(Dictionary.name == name)
        res = await self._execute(stmt)
        value = res.scalar()
        return int(value) if value is not None else None

    def get_entity_class(self) -> Type[T]:
        return Dictionary
