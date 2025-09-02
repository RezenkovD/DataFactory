from __future__ import annotations

from .domain_exception import DomainException


class NotFoundException(DomainException):
    def __init__(self, message: str, payload: dict | None = None):
        super().__init__("not_found", message, payload)
