"""API error definitions and exception handlers.

Registers FastAPI exception handlers and defines structured error
responses consistent with ERROR_CODES.md.
"""
from typing import Any, Dict, Optional

from fastapi import Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel


class ErrorDetail(BaseModel):
    """Standard error response body."""
    code: str
    message: str
    detail: Optional[Dict[str, Any]] = None
    correlation_id: Optional[str] = None


class LexCoreException(Exception):
    """Base exception for LexCore + LexRadar API."""
    def __init__(
        self,
        code: str,
        message: str,
        status_code: int = 500,
        detail: Optional[Dict[str, Any]] = None,
    ):
        self.code = code
        self.message = message
        self.status_code = status_code
        self.detail = detail
        super().__init__(message)


class TenantNotFound(LexCoreException):
    """Tenant not found in database."""
    def __init__(self, tenant_id: str):
        super().__init__(
            code="TENANT_NOT_FOUND",
            message=f"Tenant {tenant_id} not found",
            status_code=404,
        )


class AuthenticationError(LexCoreException):
    """Authentication failed."""
    def __init__(self, message: str = "Invalid credentials"):
        super().__init__(
            code="AUTHENTICATION_FAILED",
            message=message,
            status_code=401,
        )


class AuthorizationError(LexCoreException):
    """Authorization failed - insufficient permissions."""
    def __init__(self, message: str = "Insufficient permissions"):
        super().__init__(
            code="AUTHORIZATION_FAILED",
            message=message,
            status_code=403,
        )


class ResourceNotFound(LexCoreException):
    """Requested resource not found."""
    def __init__(self, resource_type: str, resource_id: str):
        super().__init__(
            code="RESOURCE_NOT_FOUND",
            message=f"{resource_type} {resource_id} not found",
            status_code=404,
        )


class ValidationError(LexCoreException):
    """Request validation failed."""
    def __init__(self, message: str, detail: Optional[Dict[str, Any]] = None):
        super().__init__(
            code="VALIDATION_ERROR",
            message=message,
            status_code=422,
            detail=detail,
        )


class RateLimitExceeded(LexCoreException):
    """Rate limit exceeded."""
    def __init__(self, limit: int, window: int):
        super().__init__(
            code="RATE_LIMIT_EXCEEDED",
            message=f"Rate limit exceeded: {limit} requests per {window} seconds",
            status_code=429,
            detail={"limit": limit, "window": window},
        )


def lexcore_exception_handler(request: Request, exc: LexCoreException) -> JSONResponse:
    """FastAPI exception handler for LexCoreException."""
    correlation_id = getattr(request.state, "correlation_id", None)
    error_detail = ErrorDetail(
        code=exc.code,
        message=exc.message,
        detail=exc.detail,
        correlation_id=correlation_id,
    )
    return JSONResponse(
        status_code=exc.status_code,
        content=error_detail.model_dump(),
    )
