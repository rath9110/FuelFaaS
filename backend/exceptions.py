from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from pydantic import ValidationError
from typing import Any
import traceback
from .logger import get_logger

logger = get_logger(__name__)


class FuelGuardException(Exception):
    """Base exception for FuelGuard application."""
    
    def __init__(self, message: str, status_code: int = 500, details: Any = None):
        self.message = message
        self.status_code = status_code
        self.details = details
        super().__init__(self.message)


class NotFoundException(FuelGuardException):
    """Resource not found exception."""
    
    def __init__(self, resource: str, identifier: str):
        message = f"{resource} with id '{identifier}' not found"
        super().__init__(message, status_code=404)


class ValidationException(FuelGuardException):
    """Validation error exception."""
    
    def __init__(self, message: str, details: Any = None):
        super().__init__(message, status_code=422, details=details)


class AuthenticationException(FuelGuardException):
    """Authentication error exception."""
    
    def __init__(self, message: str = "Authentication failed"):
        super().__init__(message, status_code=401)


class AuthorizationException(FuelGuardException):
    """Authorization error exception."""
    
    def __init__(self, message: str = "Insufficient permissions"):
        super().__init__(message, status_code=403)


class RateLimitException(FuelGuardException):
    """Rate limit exceeded exception."""
    
    def __init__(self, message: str = "Rate limit exceeded"):
        super().__init__(message, status_code=429)


async def fuelguard_exception_handler(request: Request, exc: FuelGuardException) -> JSONResponse:
    """Handle FuelGuard custom exceptions."""
    logger.error(f"FuelGuard Exception: {exc.message}", extra={
        "status_code": exc.status_code,
        "path": request.url.path,
        "details": exc.details
    })
    
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.message,
            "details": exc.details,
            "path": request.url.path
        }
    )


async def validation_exception_handler(request: Request, exc: ValidationError) -> JSONResponse:
    """Handle Pydantic validation errors."""
    logger.warning(f"Validation error: {exc.errors()}", extra={
        "path": request.url.path
    })
    
    return JSONResponse(
        status_code=422,
        content={
            "error": "Validation failed",
            "details": exc.errors(),
            "path": request.url.path
        }
    )


async def database_exception_handler(request: Request, exc: SQLAlchemyError) -> JSONResponse:
    """Handle database errors."""
    logger.error(f"Database error: {str(exc)}", extra={
        "path": request.url.path,
        "traceback": traceback.format_exc()
    })
    
    # Don't expose internal database errors to clients
    if isinstance(exc, IntegrityError):
        message = "Database integrity constraint violated. Duplicate or invalid data."
    else:
        message = "Database operation failed. Please try again later."
    
    return JSONResponse(
        status_code=500,
        content={
            "error": message,
            "path": request.url.path
        }
    )


async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle all other unhandled exceptions."""
    logger.critical(f"Unhandled exception: {str(exc)}", extra={
        "path": request.url.path,
        "traceback": traceback.format_exc()
    })
    
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "path": request.url.path
        }
    )


# Exception handlers mapping
exception_handlers = {
    FuelGuardException: fuelguard_exception_handler,
    ValidationError: validation_exception_handler,
    SQLAlchemyError: database_exception_handler,
    Exception: general_exception_handler,
}
