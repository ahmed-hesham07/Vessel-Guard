"""
Error handling and exception classes for Vessel Guard API.

This module defines custom exceptions and error handling utilities
for proper error reporting and debugging.
"""

from typing import Any, Dict, Optional, Union
from fastapi import HTTPException, status
from pydantic import BaseModel


class ErrorDetail(BaseModel):
    """Error detail model for structured error responses."""
    message: str
    code: Optional[str] = None
    field: Optional[str] = None
    details: Optional[Dict[str, Any]] = None


class ErrorResponse(BaseModel):
    """Standard error response model."""
    error: str
    message: str
    status_code: int
    details: Optional[Union[str, Dict[str, Any], list]] = None
    timestamp: Optional[str] = None
    path: Optional[str] = None


# Custom Exception Classes

class VesselGuardException(Exception):
    """Base exception for Vessel Guard application."""
    
    def __init__(
        self,
        message: str,
        error_code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.error_code = error_code
        self.details = details or {}
        super().__init__(self.message)


class ValidationError(VesselGuardException):
    """Exception raised when validation fails."""
    pass


class CalculationError(VesselGuardException):
    """Exception raised when engineering calculations fail."""
    pass


class MaterialNotFoundError(VesselGuardException):
    """Exception raised when material is not found."""
    pass


class InsufficientPermissionError(VesselGuardException):
    """Exception raised when user lacks required permissions."""
    pass


class ResourceNotFoundError(VesselGuardException):
    """Exception raised when a resource is not found."""
    pass


class DuplicateResourceError(VesselGuardException):
    """Exception raised when attempting to create duplicate resource."""
    pass


class OrganizationMismatchError(VesselGuardException):
    """Exception raised when resource doesn't belong to user's organization."""
    pass


class FileStorageError(VesselGuardException):
    """Exception raised for file storage operations."""
    pass


class EmailServiceError(VesselGuardException):
    """Exception raised for email service operations."""
    pass


class BackgroundTaskError(VesselGuardException):
    """Exception raised for background task operations."""
    pass


class DatabaseError(VesselGuardException):
    """Exception raised for database operations."""
    pass


class AuthenticationError(VesselGuardException):
    """Exception raised for authentication failures."""
    pass


class ConfigurationError(VesselGuardException):
    """Exception raised for configuration issues."""
    pass


# HTTP Exception Mappers

def validation_exception(
    message: str,
    field: Optional[str] = None,
    details: Optional[Dict[str, Any]] = None
) -> HTTPException:
    """Create HTTP exception for validation errors."""
    return HTTPException(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        detail={
            "error": "validation_error",
            "message": message,
            "field": field,
            "details": details
        }
    )


def not_found_exception(
    resource: str,
    resource_id: Optional[str] = None
) -> HTTPException:
    """Create HTTP exception for not found errors."""
    message = f"{resource} not found"
    if resource_id:
        message += f" (ID: {resource_id})"
    
    return HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail={
            "error": "resource_not_found",
            "message": message,
            "resource": resource,
            "resource_id": resource_id
        }
    )


def permission_denied_exception(
    message: str = "Insufficient permissions to perform this action"
) -> HTTPException:
    """Create HTTP exception for permission denied errors."""
    return HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail={
            "error": "permission_denied",
            "message": message
        }
    )


def duplicate_resource_exception(
    resource: str,
    field: Optional[str] = None,
    value: Optional[str] = None
) -> HTTPException:
    """Create HTTP exception for duplicate resource errors."""
    message = f"{resource} already exists"
    if field and value:
        message += f" with {field}: {value}"
    
    return HTTPException(
        status_code=status.HTTP_409_CONFLICT,
        detail={
            "error": "duplicate_resource",
            "message": message,
            "resource": resource,
            "field": field,
            "value": value
        }
    )


def calculation_error_exception(
    message: str,
    calculation_type: Optional[str] = None,
    parameters: Optional[Dict[str, Any]] = None
) -> HTTPException:
    """Create HTTP exception for calculation errors."""
    return HTTPException(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        detail={
            "error": "calculation_error",
            "message": message,
            "calculation_type": calculation_type,
            "parameters": parameters
        }
    )


def file_storage_exception(
    message: str,
    filename: Optional[str] = None,
    operation: Optional[str] = None
) -> HTTPException:
    """Create HTTP exception for file storage errors."""
    return HTTPException(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        detail={
            "error": "file_storage_error",
            "message": message,
            "filename": filename,
            "operation": operation
        }
    )


def database_exception(
    message: str = "Database operation failed"
) -> HTTPException:
    """Create HTTP exception for database errors."""
    return HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail={
            "error": "database_error",
            "message": message
        }
    )


def service_unavailable_exception(
    service: str,
    message: Optional[str] = None
) -> HTTPException:
    """Create HTTP exception for service unavailable errors."""
    if not message:
        message = f"{service} service is currently unavailable"
    
    return HTTPException(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        detail={
            "error": "service_unavailable",
            "message": message,
            "service": service
        }
    )


def rate_limit_exception(
    message: str = "Rate limit exceeded. Please try again later."
) -> HTTPException:
    """Create HTTP exception for rate limit errors."""
    return HTTPException(
        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
        detail={
            "error": "rate_limit_exceeded",
            "message": message
        }
    )


def authentication_exception(
    message: str = "Authentication required"
) -> HTTPException:
    """Create HTTP exception for authentication errors."""
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail={
            "error": "authentication_required",
            "message": message
        },
        headers={"WWW-Authenticate": "Bearer"}
    )


def organization_mismatch_exception(
    message: str = "Resource does not belong to your organization"
) -> HTTPException:
    """Create HTTP exception for organization mismatch errors."""
    return HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail={
            "error": "organization_mismatch", 
            "message": message
        }
    )


def configuration_exception(
    message: str,
    configuration_key: Optional[str] = None
) -> HTTPException:
    """Create HTTP exception for configuration errors."""
    return HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail={
            "error": "configuration_error",
            "message": message,
            "configuration_key": configuration_key
        }
    )


# Error Handler Utilities

def handle_database_error(error: Exception) -> HTTPException:
    """Handle database errors and convert to appropriate HTTP exceptions."""
    error_message = str(error)
    
    # Check for common database error patterns
    if "duplicate key" in error_message.lower():
        return duplicate_resource_exception("Resource", "key", "unknown")
    elif "not found" in error_message.lower():
        return not_found_exception("Resource")
    elif "foreign key" in error_message.lower():
        return validation_exception("Referenced resource does not exist")
    else:
        return database_exception(f"Database operation failed: {error_message}")


def handle_calculation_error(error: Exception) -> HTTPException:
    """Handle calculation errors and convert to appropriate HTTP exceptions."""
    error_message = str(error)
    
    if "division by zero" in error_message.lower():
        return calculation_error_exception("Division by zero in calculation")
    elif "invalid parameter" in error_message.lower():
        return validation_exception("Invalid calculation parameters")
    elif "out of range" in error_message.lower():
        return validation_exception("Parameter value out of acceptable range")
    else:
        return calculation_error_exception(f"Calculation failed: {error_message}")


def handle_file_operation_error(error: Exception, operation: str = "unknown") -> HTTPException:
    """Handle file operation errors and convert to appropriate HTTP exceptions."""
    error_message = str(error)
    
    if "permission denied" in error_message.lower():
        return permission_denied_exception("Insufficient permissions for file operation")
    elif "file not found" in error_message.lower():
        return not_found_exception("File")
    elif "disk full" in error_message.lower():
        return service_unavailable_exception("Storage", "Insufficient storage space")
    else:
        return file_storage_exception(f"File operation failed: {error_message}", operation=operation)


# Exception to HTTP Status Code Mapping

EXCEPTION_STATUS_MAPPING = {
    ValidationError: status.HTTP_422_UNPROCESSABLE_ENTITY,
    CalculationError: status.HTTP_422_UNPROCESSABLE_ENTITY,
    MaterialNotFoundError: status.HTTP_404_NOT_FOUND,
    InsufficientPermissionError: status.HTTP_403_FORBIDDEN,
    ResourceNotFoundError: status.HTTP_404_NOT_FOUND,
    DuplicateResourceError: status.HTTP_409_CONFLICT,
    OrganizationMismatchError: status.HTTP_403_FORBIDDEN,
    FileStorageError: status.HTTP_422_UNPROCESSABLE_ENTITY,
    EmailServiceError: status.HTTP_503_SERVICE_UNAVAILABLE,
    BackgroundTaskError: status.HTTP_500_INTERNAL_SERVER_ERROR,
    DatabaseError: status.HTTP_500_INTERNAL_SERVER_ERROR,
    AuthenticationError: status.HTTP_401_UNAUTHORIZED,
    ConfigurationError: status.HTTP_500_INTERNAL_SERVER_ERROR,
}


def convert_exception_to_http(exception: VesselGuardException) -> HTTPException:
    """Convert custom exceptions to HTTP exceptions."""
    status_code = EXCEPTION_STATUS_MAPPING.get(
        type(exception),
        status.HTTP_500_INTERNAL_SERVER_ERROR
    )
    
    return HTTPException(
        status_code=status_code,
        detail={
            "error": exception.error_code or exception.__class__.__name__.lower(),
            "message": exception.message,
            "details": exception.details
        }
    )
