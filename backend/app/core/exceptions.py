"""
Custom exception classes for the application.

These exceptions map to specific HTTP status codes and API error response formats.
"""

from typing import Any, Dict, Optional


class BaseAppException(Exception):
    """Base exception for all application errors."""
    
    def __init__(
        self,
        code: str,
        message: str,
        status_code: int = 400,
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(message)
        self.code = code
        self.message = message
        self.status_code = status_code
        self.details = details or {}


# ── Authentication & Authorization ──────────────────────────────

class AuthenticationException(BaseAppException):
    """Raised when authentication fails."""
    
    def __init__(self, message: str = "Authentication failed", details: Optional[Dict[str, Any]] = None):
        super().__init__(
            code="AUTHENTICATION_FAILED",
            message=message,
            status_code=401,
            details=details,
        )


class TokenExpiredException(BaseAppException):
    """Raised when a JWT is expired."""
    
    def __init__(self, message: str = "Token has expired", details: Optional[Dict[str, Any]] = None):
        super().__init__(
            code="TOKEN_EXPIRED",
            message=message,
            status_code=401,
            details=details,
        )


class PermissionDeniedException(BaseAppException):
    """Raised when user lacks permissions to perform action."""
    
    def __init__(self, message: str = "Permission denied", details: Optional[Dict[str, Any]] = None):
        super().__init__(
            code="PERMISSION_DENIED",
            message=message,
            status_code=403,
            details=details,
        )


# ── Not Found Errors ─────────────────────────────────────────────

class NotFoundException(BaseAppException):
    """Raised when a requested resource is not found."""
    
    def __init__(self, message: str = "Resource not found", details: Optional[Dict[str, Any]] = None):
        super().__init__(
            code="RESOURCE_NOT_FOUND",
            message=message,
            status_code=404,
            details=details,
        )


class UserNotFoundException(NotFoundException):
    def __init__(self, message: str = "User not found"):
        super().__init__(message=message)


class DatasetNotFoundException(NotFoundException):
    def __init__(self, message: str = "Dataset not found"):
        super().__init__(message=message)


class DashboardNotFoundException(NotFoundException):
    def __init__(self, message: str = "Dashboard not found"):
        super().__init__(message=message)


# ── Validation & CSV Errors ──────────────────────────────────────

class ValidationException(BaseAppException):
    """Raised when input validation fails."""
    
    def __init__(self, message: str = "Validation failed", details: Optional[Dict[str, Any]] = None):
        super().__init__(
            code="VALIDATION_FAILED",
            message=message,
            status_code=400,
            details=details,
        )


class FileTooLargeException(ValidationException):
    def __init__(self, max_size_mb: int):
        super().__init__(
            message=f"File exceeds maximum allowed size of {max_size_mb}MB",
            details={"max_size_mb": max_size_mb},
        )


class InvalidFileTypeException(ValidationException):
    def __init__(self, message: str = "Only CSV files are allowed"):
        super().__init__(message=message)


class CSVProcessingException(BaseAppException):
    """Raised when CSV processing or type inference fails."""
    
    def __init__(self, message: str = "Failed to process CSV file", details: Optional[Dict[str, Any]] = None):
        super().__init__(
            code="CSV_PROCESSING_ERROR",
            message=message,
            status_code=422,
            details=details,
        )


# ── SQL Query Errors ─────────────────────────────────────────────

class SQLSecurityException(BaseAppException):
    """Raised when a user SQL query fails security validation."""
    
    def __init__(self, message: str = "SQL query violates safety rules", details: Optional[Dict[str, Any]] = None):
        super().__init__(
            code="SQL_SECURITY_VIOLATION",
            message=message,
            status_code=400,
            details=details,
        )


class SQLExecutionException(BaseAppException):
    """Raised when a SQL query execution fails."""
    
    def __init__(self, message: str = "SQL execution failed", details: Optional[Dict[str, Any]] = None):
        super().__init__(
            code="SQL_EXECUTION_ERROR",
            message=message,
            status_code=400,
            details=details,
        )
