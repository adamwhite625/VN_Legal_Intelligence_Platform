"""
Custom exceptions for Legal Chatbot API.
"""

from typing import Optional, Any


class AppException(Exception):
    """Base exception class for the application."""

    def __init__(
        self,
        message: str,
        error_code: Optional[str] = None,
        status_code: int = 500,
        details: Optional[Any] = None,
    ):
        self.message = message
        self.error_code = error_code or "APP_ERROR"
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)


class ValidationError(AppException):
    """Raised when input validation fails."""

    def __init__(self, message: str, details: Optional[Any] = None):
        super().__init__(
            message=message,
            error_code="VALIDATION_ERROR",
            status_code=422,
            details=details,
        )


class NotFoundError(AppException):
    """Raised when a resource is not found."""

    def __init__(self, message: str, details: Optional[Any] = None):
        super().__init__(
            message=message,
            error_code="NOT_FOUND",
            status_code=404,
            details=details,
        )


class UnauthorizedError(AppException):
    """Raised when authentication fails."""

    def __init__(self, message: str = "Unauthorized", details: Optional[Any] = None):
        super().__init__(
            message=message,
            error_code="UNAUTHORIZED",
            status_code=401,
            details=details,
        )


class ForbiddenError(AppException):
    """Raised when user doesn't have permission."""

    def __init__(self, message: str = "Forbidden", details: Optional[Any] = None):
        super().__init__(
            message=message,
            error_code="FORBIDDEN",
            status_code=403,
            details=details,
        )


class ConflictError(AppException):
    """Raised when there's a conflict (e.g., duplicate entry)."""

    def __init__(self, message: str, details: Optional[Any] = None):
        super().__init__(
            message=message,
            error_code="CONFLICT",
            status_code=409,
            details=details,
        )
