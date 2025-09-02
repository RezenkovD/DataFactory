from __future__ import annotations

from .domain_exception import DomainException


class ValidationException(DomainException):
    def __init__(self, message: str, payload: dict | None = None):
        super().__init__("validation_error", message, payload)
