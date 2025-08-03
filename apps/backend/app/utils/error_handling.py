"""
Comprehensive error handling utilities for the Vessel Guard application.

Provides standardized error handling, custom exceptions, and error response formatting
for consistent API error responses across all endpoints.
"""

import traceback
from typing import Any, Dict, Optional, Union, List
from datetime import datetime
from enum import Enum

from fastapi import HTTPException, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from pydantic import ValidationError

from app.core.logging_config import get_logger

logger = get_logger('vessel_guard.error_handler')


class ErrorCode(str, Enum):
    """Standardized error codes for the application."""
    
    # Authentication & Authorization
    AUTHENTICATION_FAILED = "AUTH_001"
    INVALID_CREDENTIALS = "AUTH_002"
    TOKEN_EXPIRED = "AUTH_003"
    TOKEN_INVALID = "AUTH_004"
    INSUFFICIENT_PERMISSIONS = "AUTH_005"
    ACCOUNT_LOCKED = "AUTH_006"
    
    # Validation Errors
    VALIDATION_ERROR = "VAL_001"
    INVALID_INPUT = "VAL_002"
    MISSING_REQUIRED_FIELD = "VAL_003"
    INVALID_FORMAT = "VAL_004"
    VALUE_OUT_OF_RANGE = "VAL_005"
    
    # Resource Errors
    RESOURCE_NOT_FOUND = "RES_001"
    RESOURCE_ALREADY_EXISTS = "RES_002"
    RESOURCE_CONFLICT = "RES_003"
    RESOURCE_LOCKED = "RES_004"
    RESOURCE_QUOTA_EXCEEDED = "RES_005"
    
    # Database Errors
    DATABASE_ERROR = "DB_001"
    DATABASE_CONNECTION_ERROR = "DB_002"
    CONSTRAINT_VIOLATION = "DB_003"
    TRANSACTION_FAILED = "DB_004"
    
    # Business Logic Errors
    BUSINESS_RULE_VIOLATION = "BIZ_001"
    CALCULATION_ERROR = "BIZ_002"
    INVALID_STATE_TRANSITION = "BIZ_003"
    DEPENDENCY_VIOLATION = "BIZ_004"
    
    # External Service Errors
    EXTERNAL_SERVICE_ERROR = "EXT_001"
    EXTERNAL_SERVICE_TIMEOUT = "EXT_002"
    EXTERNAL_SERVICE_UNAVAILABLE = "EXT_003"
    
    # System Errors
    INTERNAL_SERVER_ERROR = "SYS_001"
    SERVICE_UNAVAILABLE = "SYS_002"
    RATE_LIMIT_EXCEEDED = "SYS_003"
    CONFIGURATION_ERROR = "SYS_004"


class VesselGuardException(Exception):
    """Base exception class for Vessel Guard application."""
    
    def __init__(
        self,
        message: str,
        error_code: ErrorCode = ErrorCode.INTERNAL_SERVER_ERROR,
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        details: Optional[Dict[str, Any]] = None,
        user_message: Optional[str] = None
    ):
        self.message = message
        self.error_code = error_code
        self.status_code = status_code
        self.details = details or {}
        self.user_message = user_message or message
        super().__init__(self.message)


class AuthenticationError(VesselGuardException):
    """Authentication related errors."""
    
    def __init__(
        self,
        message: str = "Authentication failed",
        error_code: ErrorCode = ErrorCode.AUTHENTICATION_FAILED,
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            message=message,
            error_code=error_code,
            status_code=status.HTTP_401_UNAUTHORIZED,
            details=details,
            user_message="Authentication required. Please log in."
        )


class AuthorizationError(VesselGuardException):
    """Authorization related errors."""
    
    def __init__(
        self,
        message: str = "Insufficient permissions",
        error_code: ErrorCode = ErrorCode.INSUFFICIENT_PERMISSIONS,
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            message=message,
            error_code=error_code,
            status_code=status.HTTP_403_FORBIDDEN,
            details=details,
            user_message="You don't have permission to perform this action."
        )


class ValidationError(VesselGuardException):
    """Validation related errors."""
    
    def __init__(
        self,
        message: str = "Validation failed",
        error_code: ErrorCode = ErrorCode.VALIDATION_ERROR,
        details: Optional[Dict[str, Any]] = None,
        field_errors: Optional[List[Dict[str, Any]]] = None
    ):
        if field_errors:
            details = details or {}
            details["field_errors"] = field_errors
        
        super().__init__(
            message=message,
            error_code=error_code,
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            details=details,
            user_message="Please check your input and try again."
        )


class ResourceNotFoundError(VesselGuardException):
    """Resource not found errors."""
    
    def __init__(
        self,
        resource_type: str,
        resource_id: Optional[Union[str, int]] = None,
        message: Optional[str] = None
    ):
        if not message:
            if resource_id:
                message = f"{resource_type} with ID '{resource_id}' not found"
            else:
                message = f"{resource_type} not found"
        
        super().__init__(
            message=message,
            error_code=ErrorCode.RESOURCE_NOT_FOUND,
            status_code=status.HTTP_404_NOT_FOUND,
            details={"resource_type": resource_type, "resource_id": resource_id},
            user_message=f"The requested {resource_type.lower()} could not be found."
        )


class ResourceConflictError(VesselGuardException):
    """Resource conflict errors."""
    
    def __init__(
        self,
        message: str,
        error_code: ErrorCode = ErrorCode.RESOURCE_CONFLICT,
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            message=message,
            error_code=error_code,
            status_code=status.HTTP_409_CONFLICT,
            details=details,
            user_message="The requested operation conflicts with the current state."
        )


class BusinessRuleViolationError(VesselGuardException):
    """Business rule violation errors."""
    
    def __init__(
        self,
        message: str,
        rule_name: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        if rule_name:
            details = details or {}
            details["violated_rule"] = rule_name
        
        super().__init__(
            message=message,
            error_code=ErrorCode.BUSINESS_RULE_VIOLATION,
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            details=details,
            user_message="The operation violates business rules."
        )


class CalculationError(VesselGuardException):
    """Calculation related errors."""
    
    def __init__(
        self,
        message: str,
        calculation_type: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        if calculation_type:
            details = details or {}
            details["calculation_type"] = calculation_type
        
        super().__init__(
            message=message,
            error_code=ErrorCode.CALCULATION_ERROR,
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            details=details,
            user_message="Unable to perform the requested calculation."
        )


class ExternalServiceError(VesselGuardException):
    """External service related errors."""
    
    def __init__(
        self,
        message: str,
        service_name: Optional[str] = None,
        error_code: ErrorCode = ErrorCode.EXTERNAL_SERVICE_ERROR,
        details: Optional[Dict[str, Any]] = None
    ):
        if service_name:
            details = details or {}
            details["service_name"] = service_name
        
        super().__init__(
            message=message,
            error_code=error_code,
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            details=details,
            user_message="An external service is currently unavailable."
        )


def format_error_response(
    error_code: ErrorCode,
    message: str,
    status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
    details: Optional[Dict[str, Any]] = None,
    user_message: Optional[str] = None,
    request_id: Optional[str] = None
) -> Dict[str, Any]:
    """Format a standardized error response."""
    
    response = {
        "error": {
            "code": error_code.value,
            "message": message,
            "user_message": user_message or message,
            "timestamp": datetime.utcnow().isoformat(),
            "status_code": status_code
        }
    }
    
    if details:
        response["error"]["details"] = details
    
    if request_id:
        response["error"]["request_id"] = request_id
    
    return response


def format_validation_error_response(
    validation_errors: List[Dict[str, Any]],
    request_id: Optional[str] = None
) -> Dict[str, Any]:
    """Format validation error response with field-specific errors."""
    
    # Extract field errors for better UX
    field_errors = []
    for error in validation_errors:
        field_error = {
            "field": ".".join(str(loc) for loc in error.get("loc", [])),
            "message": error.get("msg", "Invalid value"),
            "type": error.get("type", "validation_error"),
            "input": error.get("input")
        }
        field_errors.append(field_error)
    
    return format_error_response(
        error_code=ErrorCode.VALIDATION_ERROR,
        message="Validation failed",
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        details={"field_errors": field_errors},
        user_message="Please check your input and correct any validation errors.",
        request_id=request_id
    )


def create_error_handler():
    """Create error handler functions for FastAPI application."""
    
    async def vessel_guard_exception_handler(request: Request, exc: VesselGuardException) -> JSONResponse:
        """Handle custom VesselGuard exceptions."""
        
        request_id = getattr(request.state, "request_id", None)
        
        # Log the error
        logger.error(
            f"VesselGuard exception: {exc.error_code.value} - {exc.message}",
            extra={
                "error_code": exc.error_code.value,
                "status_code": exc.status_code,
                "details": exc.details,
                "request_id": request_id,
                "path": request.url.path,
                "method": request.method
            }
        )
        
        response_data = format_error_response(
            error_code=exc.error_code,
            message=exc.message,
            status_code=exc.status_code,
            details=exc.details,
            user_message=exc.user_message,
            request_id=request_id
        )
        
        return JSONResponse(
            status_code=exc.status_code,
            content=response_data
        )
    
    async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
        """Handle FastAPI HTTP exceptions."""
        
        request_id = getattr(request.state, "request_id", None)
        
        # Map status codes to error codes
        error_code_map = {
            401: ErrorCode.AUTHENTICATION_FAILED,
            403: ErrorCode.INSUFFICIENT_PERMISSIONS,
            404: ErrorCode.RESOURCE_NOT_FOUND,
            409: ErrorCode.RESOURCE_CONFLICT,
            422: ErrorCode.VALIDATION_ERROR,
            429: ErrorCode.RATE_LIMIT_EXCEEDED,
            500: ErrorCode.INTERNAL_SERVER_ERROR,
            503: ErrorCode.SERVICE_UNAVAILABLE
        }
        
        error_code = error_code_map.get(exc.status_code, ErrorCode.INTERNAL_SERVER_ERROR)
        
        logger.warning(
            f"HTTP exception: {exc.status_code} - {exc.detail}",
            extra={
                "status_code": exc.status_code,
                "detail": exc.detail,
                "request_id": request_id,
                "path": request.url.path,
                "method": request.method
            }
        )
        
        response_data = format_error_response(
            error_code=error_code,
            message=str(exc.detail),
            status_code=exc.status_code,
            request_id=request_id
        )
        
        return JSONResponse(
            status_code=exc.status_code,
            content=response_data
        )
    
    async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
        """Handle Pydantic validation exceptions."""
        
        request_id = getattr(request.state, "request_id", None)
        
        logger.warning(
            f"Validation error: {len(exc.errors())} validation errors",
            extra={
                "validation_errors": exc.errors(),
                "request_id": request_id,
                "path": request.url.path,
                "method": request.method
            }
        )
        
        response_data = format_validation_error_response(
            validation_errors=exc.errors(),
            request_id=request_id
        )
        
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content=response_data
        )
    
    async def sqlalchemy_exception_handler(request: Request, exc: SQLAlchemyError) -> JSONResponse:
        """Handle SQLAlchemy database exceptions."""
        
        request_id = getattr(request.state, "request_id", None)
        
        # Determine error type
        if isinstance(exc, IntegrityError):
            error_code = ErrorCode.CONSTRAINT_VIOLATION
            status_code = status.HTTP_409_CONFLICT
            user_message = "The operation conflicts with existing data."
        else:
            error_code = ErrorCode.DATABASE_ERROR
            status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
            user_message = "A database error occurred."
        
        logger.error(
            f"Database error: {type(exc).__name__} - {str(exc)}",
            extra={
                "error_type": type(exc).__name__,
                "request_id": request_id,
                "path": request.url.path,
                "method": request.method
            }
        )
        
        response_data = format_error_response(
            error_code=error_code,
            message=str(exc),
            status_code=status_code,
            user_message=user_message,
            request_id=request_id
        )
        
        return JSONResponse(
            status_code=status_code,
            content=response_data
        )
    
    async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        """Handle any unhandled exceptions."""
        
        request_id = getattr(request.state, "request_id", None)
        
        # Get full traceback for logging
        tb_str = traceback.format_exc()
        
        logger.error(
            f"Unhandled exception: {type(exc).__name__} - {str(exc)}",
            extra={
                "error_type": type(exc).__name__,
                "traceback": tb_str,
                "request_id": request_id,
                "path": request.url.path,
                "method": request.method
            }
        )
        
        response_data = format_error_response(
            error_code=ErrorCode.INTERNAL_SERVER_ERROR,
            message="An unexpected error occurred",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            user_message="An unexpected error occurred. Please try again later.",
            request_id=request_id
        )
        
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=response_data
        )
    
    return {
        "vessel_guard_exception": vessel_guard_exception_handler,
        "http_exception": http_exception_handler,
        "validation_exception": validation_exception_handler,
        "sqlalchemy_exception": sqlalchemy_exception_handler,
        "generic_exception": generic_exception_handler
    }


# Utility functions for common error scenarios

def raise_not_found(resource_type: str, resource_id: Optional[Union[str, int]] = None) -> None:
    """Raise a standardized not found error."""
    raise ResourceNotFoundError(resource_type, resource_id)


def raise_already_exists(resource_type: str, identifier: str) -> None:
    """Raise a standardized resource already exists error."""
    raise ResourceConflictError(
        message=f"{resource_type} with identifier '{identifier}' already exists",
        details={"resource_type": resource_type, "identifier": identifier}
    )


def raise_validation_error(message: str, field: Optional[str] = None) -> None:
    """Raise a standardized validation error."""
    field_errors = []
    if field:
        field_errors.append({
            "field": field,
            "message": message,
            "type": "value_error"
        })
    
    raise ValidationError(
        message=message,
        field_errors=field_errors if field_errors else None
    )


def raise_business_rule_violation(message: str, rule_name: Optional[str] = None) -> None:
    """Raise a standardized business rule violation error."""
    raise BusinessRuleViolationError(message, rule_name)


def raise_calculation_error(message: str, calculation_type: Optional[str] = None) -> None:
    """Raise a standardized calculation error."""
    raise CalculationError(message, calculation_type)
