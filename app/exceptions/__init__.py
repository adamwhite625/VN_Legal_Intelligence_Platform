"""
Exception imports for Legal Chatbot API.
"""

from app.exceptions.base import (
    AppException,
    ValidationError,
    NotFoundError,
    UnauthorizedError,
    ForbiddenError,
    ConflictError,
)
from app.exceptions.handlers import setup_exception_handlers

__all__ = [
    "AppException",
    "ValidationError",
    "NotFoundError",
    "UnauthorizedError",
    "ForbiddenError",
    "ConflictError",
    "setup_exception_handlers",
]
