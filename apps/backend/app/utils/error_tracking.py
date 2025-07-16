"""
Error tracking utilities for common error scenarios.

Provides convenient functions for tracking errors in specific contexts
like API endpoints, database operations, authentication, etc.
"""

import inspect
import traceback
from functools import wraps
from typing import Any, Dict, Optional, Callable
from contextlib import contextmanager
from fastapi import Request, HTTPException

from app.core.logging_config import (
    log_error, log_exception, log_database_error, 
    log_authentication_error, log_critical_error, get_logger
)


class ErrorTracker:
    """Context manager and utility class for error tracking."""
    
    def __init__(self, operation_name: str, context: Dict[str, Any] = None):
        self.operation_name = operation_name
        self.context = context or {}
        self.logger = get_logger('vessel_guard.error_tracker')
    
    def __enter__(self):
        self.logger.debug(f"Starting operation: {self.operation_name}", extra=self.context)
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            # An exception occurred
            error_context = {
                **self.context,
                'operation': self.operation_name,
                'exception_type': exc_type.__name__,
                'exception_message': str(exc_val),
                'traceback': traceback.format_exc()
            }
            
            log_exception(
                exception=exc_val,
                context=error_context,
                location=self.operation_name
            )
        else:
            self.logger.debug(f"Completed operation: {self.operation_name}", extra=self.context)
        
        return False  # Don't suppress exceptions
    
    def log_error(self, error_type: str, message: str, details: Dict[str, Any] = None):
        """Log an error within this operation context."""
        error_context = {**self.context, **(details or {})}
        log_error(
            error_type=error_type,
            message=message,
            details=error_context,
            location=self.operation_name
        )


@contextmanager
def track_operation(operation_name: str, context: Dict[str, Any] = None):
    """Context manager for tracking operations."""
    tracker = ErrorTracker(operation_name, context)
    try:
        yield tracker
    finally:
        pass


def track_api_errors(operation_name: str = None):
    """Decorator for API endpoint error tracking."""
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            op_name = operation_name or f"api.{func.__name__}"
            
            # Try to extract request from arguments
            request = None
            for arg in args:
                if isinstance(arg, Request):
                    request = arg
                    break
            
            context = {
                'endpoint': func.__name__,
                'function_module': func.__module__
            }
            
            if request:
                context.update({
                    'method': request.method,
                    'path': request.url.path,
                    'client_ip': request.client.host if request.client else None
                })
            
            try:
                return await func(*args, **kwargs)
            except HTTPException as e:
                # HTTP exceptions are expected, log them appropriately
                if e.status_code >= 500:
                    log_error(
                        error_type='api_server_error',
                        message=f"HTTP {e.status_code}: {e.detail}",
                        details=context,
                        location=op_name
                    )
                raise
            except Exception as e:
                # Unexpected exceptions
                log_exception(
                    exception=e,
                    context=context,
                    location=op_name
                )
                raise
        
        return wrapper
    return decorator


def track_database_errors(table_name: str = None):
    """Decorator for database operation error tracking."""
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            table = table_name or 'unknown'
            operation = func.__name__
            
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                log_database_error(
                    operation=operation,
                    table=table,
                    error=e,
                    query=None,  # Could be extracted from ORM
                    params=kwargs
                )
                raise
        
        return wrapper
    return decorator


def track_auth_errors(auth_type: str = None):
    """Decorator for authentication operation error tracking."""
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            auth_operation = auth_type or func.__name__
            
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                # Extract IP and user agent if available
                ip_address = None
                user_agent = None
                
                for arg in args:
                    if isinstance(arg, Request):
                        ip_address = arg.client.host if arg.client else None
                        user_agent = arg.headers.get('user-agent')
                        break
                
                log_authentication_error(
                    error_type=auth_operation,
                    details={
                        'function': func.__name__,
                        'exception_type': type(e).__name__,
                        'exception_message': str(e)
                    },
                    ip_address=ip_address,
                    user_agent=user_agent
                )
                raise
        
        return wrapper
    return decorator


class ErrorMetrics:
    """Class to track error metrics and patterns."""
    
    def __init__(self):
        self.logger = get_logger('vessel_guard.error_metrics')
    
    def log_error_pattern(self, pattern_type: str, details: Dict[str, Any]):
        """Log error patterns for analysis."""
        self.logger.warning(
            f"Error pattern detected: {pattern_type}",
            extra={
                'pattern_type': pattern_type,
                'error_pattern': True,
                **details
            }
        )
    
    def log_error_spike(self, error_type: str, count: int, time_window: str):
        """Log error spikes for monitoring."""
        self.logger.error(
            f"Error spike detected: {error_type}",
            extra={
                'error_type': error_type,
                'error_count': count,
                'time_window': time_window,
                'error_spike': True,
                'requires_attention': True
            }
        )
    
    def log_recurring_error(self, error_signature: str, occurrences: int):
        """Log recurring errors."""
        self.logger.warning(
            f"Recurring error: {error_signature}",
            extra={
                'error_signature': error_signature,
                'occurrences': occurrences,
                'recurring_error': True
            }
        )


def handle_startup_errors(component_name: str):
    """Decorator for handling startup errors."""
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                from app.core.logging_config import log_startup_error
                
                # Determine if error is fatal
                fatal = 'database' in component_name.lower() or 'config' in component_name.lower()
                
                log_startup_error(
                    component=component_name,
                    error=e,
                    fatal=fatal
                )
                
                if fatal:
                    raise  # Re-raise fatal errors
                else:
                    # Log but don't crash for non-fatal errors
                    logger = get_logger('vessel_guard.startup')
                    logger.warning(f"Non-fatal startup error in {component_name}, continuing...")
                    return None
        
        return wrapper
    return decorator


def log_user_error(user_id: str, error_type: str, details: Dict[str, Any] = None):
    """Log user-specific errors."""
    logger = get_logger('vessel_guard.user_errors')
    
    error_context = {
        'user_id': user_id,
        'error_type': error_type,
        'user_error': True,
        **(details or {})
    }
    
    logger.warning(f"User error: {error_type} for user {user_id}", extra=error_context)


def log_business_logic_error(operation: str, entity: str, details: Dict[str, Any] = None):
    """Log business logic errors."""
    logger = get_logger('vessel_guard.business_errors')
    
    error_context = {
        'operation': operation,
        'entity': entity,
        'business_logic_error': True,
        **(details or {})
    }
    
    logger.error(f"Business logic error: {operation} on {entity}", extra=error_context)


def log_validation_failure(field: str, value: Any, rule: str, details: Dict[str, Any] = None):
    """Log validation failures."""
    logger = get_logger('vessel_guard.validation_errors')
    
    # Sanitize value for logging
    safe_value = str(value)[:100] if value is not None else None
    
    error_context = {
        'field': field,
        'value': safe_value,
        'validation_rule': rule,
        'validation_error': True,
        **(details or {})
    }
    
    logger.warning(f"Validation failure: {field} failed rule {rule}", extra=error_context)


def log_security_incident(incident_type: str, details: Dict[str, Any] = None, 
                         severity: str = 'HIGH'):
    """Log security incidents."""
    logger = get_logger('vessel_guard.security_incidents')
    
    incident_context = {
        'incident_type': incident_type,
        'severity': severity,
        'security_incident': True,
        'requires_immediate_attention': severity in ['HIGH', 'CRITICAL'],
        **(details or {})
    }
    
    if severity == 'CRITICAL':
        logger.critical(f"CRITICAL security incident: {incident_type}", extra=incident_context)
    elif severity == 'HIGH':
        logger.error(f"Security incident: {incident_type}", extra=incident_context)
    else:
        logger.warning(f"Security incident: {incident_type}", extra=incident_context)


# Initialize error metrics instance
error_metrics = ErrorMetrics()


def create_error_context(request: Request = None, user_id: str = None, 
                        operation: str = None) -> Dict[str, Any]:
    """Create standard error context from request and user information."""
    context = {}
    
    if request:
        context.update({
            'method': request.method,
            'path': request.url.path,
            'client_ip': request.client.host if request.client else None,
            'user_agent': request.headers.get('user-agent'),
            'request_id': getattr(request.state, 'request_id', None)
        })
    
    if user_id:
        context['user_id'] = user_id
    
    if operation:
        context['operation'] = operation
    
    return context
