from .domain_exception import DomainException
from .not_found import NotFoundException


class ValidationException(DomainException):
    def __init__(self, message: str, payload: dict | None = None):
        super().__init__("validation_error", message, payload)
