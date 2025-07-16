"""
Error logging middleware for comprehensive error tracking.

Automatically captures and logs all errors with context information
including request details, user information, and stack traces.
"""

import time
import traceback
import uuid
from typing import Dict, Any
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
from fastapi import HTTPException
from fastapi.responses import JSONResponse

from app.core.logging_config import (
    log_error, log_exception, log_authentication_error, 
    log_critical_error, get_logger
)


class ErrorLoggingMiddleware(BaseHTTPMiddleware):
    """Middleware to capture and log all application errors."""
    
    def __init__(self, app, log_all_requests: bool = False):
        super().__init__(app)
        self.log_all_requests = log_all_requests
        self.logger = get_logger('vessel_guard.middleware.error')
    
    async def dispatch(self, request: Request, call_next):
        """Process request and capture any errors."""
        # Generate unique request ID
        request_id = str(uuid.uuid4())
        start_time = time.time()
        
        # Extract request context
        request_context = self._extract_request_context(request, request_id)
        
        try:
            # Log incoming request if enabled
            if self.log_all_requests:
                self._log_request(request_context)
            
            # Process request
            response = await call_next(request)
            
            # Calculate duration
            duration_ms = round((time.time() - start_time) * 1000, 2)
            
            # Log response
            self._log_response(request_context, response, duration_ms)
            
            return response
            
        except HTTPException as e:
            # Handle HTTP exceptions (4xx, 5xx)
            duration_ms = round((time.time() - start_time) * 1000, 2)
            await self._handle_http_exception(e, request_context, duration_ms)
            raise
            
        except Exception as e:
            # Handle unexpected exceptions
            duration_ms = round((time.time() - start_time) * 1000, 2)
            await self._handle_unexpected_exception(e, request_context, duration_ms)
            
            # Return generic error response
            return JSONResponse(
                status_code=500,
                content={"detail": "Internal server error", "request_id": request_id}
            )
    
    def _extract_request_context(self, request: Request, request_id: str) -> Dict[str, Any]:
        """Extract relevant context from the request."""
        return {
            'request_id': request_id,
            'method': request.method,
            'url': str(request.url),
            'path': request.url.path,
            'query_params': dict(request.query_params),
            'headers': dict(request.headers),
            'client_ip': request.client.host if request.client else None,
            'user_agent': request.headers.get('user-agent'),
            'content_type': request.headers.get('content-type'),
            'content_length': request.headers.get('content-length'),
            'timestamp': time.time()
        }
    
    def _log_request(self, context: Dict[str, Any]):
        """Log incoming request details."""
        self.logger.info(
            f"Incoming request: {context['method']} {context['path']}",
            extra={
                **context,
                'event_type': 'request_received'
            }
        )
    
    def _log_response(self, context: Dict[str, Any], response: Response, duration_ms: float):
        """Log response details."""
        status_code = response.status_code
        
        # Determine log level based on status code
        if status_code >= 500:
            log_level = 'error'
        elif status_code >= 400:
            log_level = 'warning'
        else:
            log_level = 'info'
        
        log_func = getattr(self.logger, log_level)
        log_func(
            f"Response: {context['method']} {context['path']} - {status_code}",
            extra={
                **context,
                'status_code': status_code,
                'duration_ms': duration_ms,
                'event_type': 'response_sent',
                'performance_metric': True
            }
        )
    
    async def _handle_http_exception(self, exception: HTTPException, 
                                   context: Dict[str, Any], duration_ms: float):
        """Handle HTTP exceptions with appropriate logging."""
        error_context = {
            **context,
            'duration_ms': duration_ms,
            'status_code': exception.status_code,
            'exception_detail': exception.detail
        }
        
        if exception.status_code == 401:
            # Authentication error
            log_authentication_error(
                error_type='unauthorized_access',
                details=error_context,
                ip_address=context.get('client_ip'),
                user_agent=context.get('user_agent')
            )
        elif exception.status_code == 403:
            # Authorization error
            log_authentication_error(
                error_type='forbidden_access',
                details=error_context,
                ip_address=context.get('client_ip'),
                user_agent=context.get('user_agent')
            )
        elif exception.status_code >= 500:
            # Server error
            log_error(
                error_type='http_server_error',
                message=f"HTTP {exception.status_code}: {exception.detail}",
                details=error_context,
                location=f"{context['method']} {context['path']}",
                request_id=context['request_id']
            )
        else:
            # Client error (4xx)
            log_error(
                error_type='http_client_error',
                message=f"HTTP {exception.status_code}: {exception.detail}",
                details=error_context,
                location=f"{context['method']} {context['path']}",
                request_id=context['request_id']
            )
    
    async def _handle_unexpected_exception(self, exception: Exception, 
                                         context: Dict[str, Any], duration_ms: float):
        """Handle unexpected exceptions with comprehensive logging."""
        error_context = {
            **context,
            'duration_ms': duration_ms,
            'traceback': traceback.format_exc(),
            'exception_type': type(exception).__name__,
            'exception_message': str(exception)
        }
        
        # Log as critical error since it's unexpected
        log_critical_error(
            error_type='unexpected_exception',
            message=f"Unexpected error in {context['method']} {context['path']}: {str(exception)}",
            details=error_context,
            location=f"{context['method']} {context['path']}",
            requires_immediate_attention=True
        )
        
        # Also log the exception with traceback
        log_exception(
            exception=exception,
            context=error_context,
            location=f"{context['method']} {context['path']}",
            request_id=context['request_id']
        )


class DatabaseErrorMiddleware:
    """Middleware specifically for database error handling."""
    
    def __init__(self):
        self.logger = get_logger('vessel_guard.middleware.database')
    
    async def __call__(self, request: Request, call_next):
        """Handle database-specific errors."""
        try:
            return await call_next(request)
        except Exception as e:
            # Check if it's a database-related error
            if self._is_database_error(e):
                await self._handle_database_error(e, request)
            raise
    
    def _is_database_error(self, exception: Exception) -> bool:
        """Check if the exception is database-related."""
        error_types = [
            'OperationalError',
            'DatabaseError',
            'IntegrityError',
            'DataError',
            'InterfaceError',
            'InternalError',
            'ProgrammingError',
            'NotSupportedError'
        ]
        
        return any(error_type in str(type(exception)) for error_type in error_types)
    
    async def _handle_database_error(self, exception: Exception, request: Request):
        """Handle database errors with specific logging."""
        from app.core.logging_config import log_database_error
        
        # Extract operation and table from the request path
        path_parts = request.url.path.split('/')
        operation = request.method.lower()
        table = 'unknown'
        
        # Try to extract table/entity from path
        if len(path_parts) > 2:
            table = path_parts[2]  # Assuming /api/v1/entity format
        
        log_database_error(
            operation=operation,
            table=table,
            error=exception,
            query=None,  # Would need to be extracted from the ORM
            params=dict(request.query_params)
        )


def setup_error_logging_middleware(app, log_all_requests: bool = False):
    """Setup error logging middleware for the application."""
    app.add_middleware(ErrorLoggingMiddleware, log_all_requests=log_all_requests)
    
    # Log setup
    logger = get_logger('vessel_guard.middleware.setup')
    logger.info(
        "Error logging middleware configured",
        extra={
            'log_all_requests': log_all_requests,
            'middleware_type': 'error_logging'
        }
    )
