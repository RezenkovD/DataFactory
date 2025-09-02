from __future__ import annotations


class DomainException(Exception):
    code: str
    message: str
    payload: dict

    def __init__(self, code: str, message: str, payload: dict | None = None):
        self.code = code
        self.message = message
        self.payload = payload or {}
