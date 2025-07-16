"""
Enhanced logging configuration for Vessel Guard API.

Provides structured logging with monitoring integration, performance tracking,
and follows Azure best practices for observability.
"""

import logging
import logging.config
import sys
import os
from datetime import datetime
from typing import Any, Dict
from pathlib import Path
from pythonjsonlogger import jsonlogger
from rich.logging import RichHandler
from rich.console import Console

from app.core.config import settings


class StructuredFormatter(jsonlogger.JsonFormatter):
    """Enhanced JSON formatter with comprehensive context fields."""
    
    def add_fields(self, log_record: Dict[str, Any], record: logging.LogRecord, message_dict: Dict[str, Any]) -> None:
        """Add custom fields to log record."""
        super().add_fields(log_record, record, message_dict)
        
        # Add timestamp
        if not log_record.get('timestamp'):
            log_record['timestamp'] = datetime.utcnow().isoformat() + 'Z'
        
        # Add application context
        log_record['service'] = 'vessel-guard-api'
        log_record['version'] = getattr(settings, 'VERSION', '1.0.0')
        log_record['environment'] = getattr(settings, 'ENVIRONMENT', 'development')
        
        # Add level name if not present
        if not log_record.get('level'):
            log_record['level'] = record.levelname
        
        # Add correlation ID if available
        if hasattr(record, 'correlation_id'):
            log_record['correlation_id'] = record.correlation_id
        
        # Add user context if available
        if hasattr(record, 'user_id'):
            log_record['user_id'] = record.user_id
        
        # Add request context if available
        if hasattr(record, 'request_id'):
            log_record['request_id'] = record.request_id
        
        # Add performance metrics if available
        if hasattr(record, 'duration_ms'):
            log_record['duration_ms'] = record.duration_ms
            log_record['performance_metric'] = True
        
        # Add security context if available
        if hasattr(record, 'security_event'):
            log_record['security_event'] = record.security_event
        
        # Add business context if available
        if hasattr(record, 'business_event'):
            log_record['business_event'] = record.business_event


def setup_logging() -> None:
    """Configure comprehensive application logging."""
    
    # Determine environment
    environment = getattr(settings, 'ENVIRONMENT', 'development')
    is_production = environment in ['production', 'staging']
    debug_mode = getattr(settings, 'DEBUG', not is_production)
    log_level = getattr(settings, 'LOG_LEVEL', 'INFO').upper()
    
    # Create logs directory
    log_dir = Path('logs')
    log_dir.mkdir(exist_ok=True)
    
    # Configure logging
    config = {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'json': {
                '()': StructuredFormatter,
                'format': '%(timestamp)s %(level)s %(name)s %(message)s',
            },
            'detailed': {
                'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s [%(filename)s:%(lineno)d]',
                'datefmt': '%Y-%m-%d %H:%M:%S'
            },
            'simple': {
                'format': '%(levelname)s - %(message)s'
            }
        },
        'handlers': {
            'console': {
                'class': 'logging.StreamHandler',
                'level': log_level,
                'formatter': 'json' if is_production else 'detailed',
                'stream': sys.stdout
            }
        },
        'loggers': {
            'vessel_guard': {
                'level': log_level,
                'handlers': ['console'],
                'propagate': False
            },
            'app': {
                'level': 'DEBUG' if debug_mode else 'INFO',
                'handlers': ['console'],
                'propagate': False
            },
            'uvicorn': {
                'level': 'INFO',
                'handlers': ['console'],
                'propagate': False
            },
            'uvicorn.access': {
                'level': 'WARNING' if is_production else 'INFO',
                'handlers': ['console'],
                'propagate': False
            },
            'sqlalchemy.engine': {
                'level': 'WARNING',
                'handlers': ['console'],
                'propagate': False
            },
            'alembic': {
                'level': 'INFO',
                'handlers': ['console'],
                'propagate': False
            }
        },
        'root': {
            'level': log_level,
            'handlers': ['console']
        }
    }
    
    # Add comprehensive file logging for all environments
    # Main application log file
    config['handlers']['file'] = {
        'class': 'logging.handlers.RotatingFileHandler',
        'level': log_level,
        'formatter': 'json' if is_production else 'detailed',
        'filename': log_dir / 'vessel_guard.log',
        'maxBytes': 10485760,  # 10MB
        'backupCount': 5,
        'encoding': 'utf8'
    }
    
    # Error-specific log file
    config['handlers']['error_file'] = {
        'class': 'logging.handlers.RotatingFileHandler',
        'level': 'ERROR',
        'formatter': 'json' if is_production else 'detailed',
        'filename': log_dir / 'errors.log',
        'maxBytes': 10485760,  # 10MB
        'backupCount': 10,  # Keep more error logs
        'encoding': 'utf8'
    }
    
    # Security events log file
    config['handlers']['security_file'] = {
        'class': 'logging.handlers.RotatingFileHandler',
        'level': 'INFO',
        'formatter': 'json',
        'filename': log_dir / 'security.log',
        'maxBytes': 5242880,  # 5MB
        'backupCount': 10,
        'encoding': 'utf8'
    }
    
    # API access log file
    config['handlers']['api_file'] = {
        'class': 'logging.handlers.RotatingFileHandler',
        'level': 'INFO',
        'formatter': 'json' if is_production else 'detailed',
        'filename': log_dir / 'api_access.log',
        'maxBytes': 10485760,  # 10MB
        'backupCount': 5,
        'encoding': 'utf8'
    }
    
    # Database operations log file
    config['handlers']['db_file'] = {
        'class': 'logging.handlers.RotatingFileHandler',
        'level': 'INFO',
        'formatter': 'json' if is_production else 'detailed',
        'filename': log_dir / 'database.log',
        'maxBytes': 5242880,  # 5MB
        'backupCount': 5,
        'encoding': 'utf8'
    }
    
    # Add file handlers to all loggers
    for logger_config in config['loggers'].values():
        logger_config['handlers'].extend(['file', 'error_file'])
    config['root']['handlers'].extend(['file', 'error_file'])
    
    # Add specialized handlers for specific loggers
    config['loggers']['vessel_guard.security'] = {
        'level': 'INFO',
        'handlers': ['console', 'file', 'error_file', 'security_file'],
        'propagate': False
    }
    
    config['loggers']['vessel_guard.api'] = {
        'level': 'INFO',
        'handlers': ['console', 'file', 'error_file', 'api_file'],
        'propagate': False
    }
    
    config['loggers']['vessel_guard.database'] = {
        'level': 'INFO',
        'handlers': ['console', 'file', 'error_file', 'db_file'],
        'propagate': False
    }
    
    # Use rich handler in development
    if not is_production and sys.stdout.isatty():
        config['handlers']['console'] = {
            '()': RichHandler,
            'level': log_level,
            'rich_tracebacks': True,
            'markup': True,
            'show_time': True,
            'show_level': True,
            'show_path': True,
            'console': Console(stderr=True)
        }
    
    # Apply configuration
    logging.config.dictConfig(config)
    
    # Log setup completion
    logger = logging.getLogger('vessel_guard.setup')
    logger.info(
        "Logging configured",
        extra={
            'environment': environment,
            'log_level': log_level,
            'json_enabled': is_production,
            'file_logging': is_production,
            'debug_mode': debug_mode
        }
    )


class StructuredLogger:
    """Enhanced logger with context management and specialized logging methods."""
    
    def __init__(self, name: str):
        self.logger = logging.getLogger(name)
        self._extra_context = {}
    
    def add_context(self, **kwargs) -> 'StructuredLogger':
        """Add context to all subsequent log messages."""
        new_logger = StructuredLogger(self.logger.name)
        new_logger._extra_context = {**self._extra_context, **kwargs}
        return new_logger
    
    def _log(self, level: int, message: str, *args, **kwargs):
        """Internal logging method with context injection."""
        extra = {**self._extra_context, **kwargs.get('extra', {})}
        kwargs['extra'] = extra
        self.logger.log(level, message, *args, **kwargs)
    
    def debug(self, message: str, *args, **kwargs):
        self._log(logging.DEBUG, message, *args, **kwargs)
    
    def info(self, message: str, *args, **kwargs):
        self._log(logging.INFO, message, *args, **kwargs)
    
    def warning(self, message: str, *args, **kwargs):
        self._log(logging.WARNING, message, *args, **kwargs)
    
    def error(self, message: str, *args, **kwargs):
        self._log(logging.ERROR, message, *args, **kwargs)
    
    def critical(self, message: str, *args, **kwargs):
        self._log(logging.CRITICAL, message, *args, **kwargs)
    
    def exception(self, message: str, *args, **kwargs):
        kwargs['exc_info'] = True
        self._log(logging.ERROR, message, *args, **kwargs)


def get_logger(name: str) -> StructuredLogger:
    """Get a structured logger instance."""
    return StructuredLogger(name)


# Specialized logging functions

def log_performance(func_name: str, duration_ms: float, **context):
    """Log performance metrics."""
    logger = get_logger('vessel_guard.performance')
    logger.info(
        f"Function execution: {func_name}",
        extra={
            'function_name': func_name,
            'duration_ms': duration_ms,
            'performance_metric': True,
            **context
        }
    )


def log_security_event(event_type: str, details: Dict[str, Any], severity: str = 'INFO'):
    """Log security-related events."""
    logger = get_logger('vessel_guard.security')
    
    log_func = getattr(logger, severity.lower(), logger.info)
    log_func(
        f"Security event: {event_type}",
        extra={
            'event_type': event_type,
            'security_event': True,
            'severity': severity,
            **details
        }
    )


def log_business_event(event_type: str, details: Dict[str, Any]):
    """Log business logic events."""
    logger = get_logger('vessel_guard.business')
    logger.info(
        f"Business event: {event_type}",
        extra={
            'event_type': event_type,
            'business_event': True,
            **details
        }
    )


def log_calculation(calculation_type: str, details: Dict[str, Any]):
    """Log engineering calculation events."""
    logger = get_logger('vessel_guard.calculations')
    logger.info(
        f"Calculation performed: {calculation_type}",
        extra={
            'calculation_type': calculation_type,
            'calculation_event': True,
            **details
        }
    )


def log_database_operation(operation: str, table: str, duration_ms: float = None, **context):
    """Log database operations."""
    logger = get_logger('vessel_guard.database')
    
    extra = {
        'operation': operation,
        'table': table,
        'database_operation': True,
        **context
    }
    
    if duration_ms:
        extra['duration_ms'] = duration_ms
        extra['performance_metric'] = True
    
    logger.info(f"Database {operation}: {table}", extra=extra)


def log_api_request(method: str, path: str, status_code: int, duration_ms: float, **context):
    """Log API request details."""
    logger = get_logger('vessel_guard.api')
    
    level = logging.INFO
    if status_code >= 500:
        level = logging.ERROR
    elif status_code >= 400:
        level = logging.WARNING
    
    logger._log(
        level,
        f"{method} {path} - {status_code}",
        extra={
            'method': method,
            'path': path,
            'status_code': status_code,
            'duration_ms': duration_ms,
            'api_request': True,
            'performance_metric': True,
            **context
        }
    )


# Legacy function for backward compatibility
def get_logger_old(name: str) -> logging.Logger:
    """Get a standard logger instance (backward compatibility)."""
    return logging.getLogger(name)
    """Get a logger with the specified name."""
    return logging.getLogger(f"app.{name}")


# Logging utilities for request correlation
class ContextFilter(logging.Filter):
    """Filter to add request context to log records."""
    
    def __init__(self, correlation_id: str = None, user_id: str = None):
        super().__init__()
        self.correlation_id = correlation_id
        self.user_id = user_id
    
    def filter(self, record: logging.LogRecord) -> bool:
        """Add context to log record."""
        if self.correlation_id:
            record.correlation_id = self.correlation_id
        if self.user_id:
            record.user_id = self.user_id
        return True


def add_request_context(logger: logging.Logger, correlation_id: str = None, user_id: str = None) -> None:
    """Add request context to logger."""
    context_filter = ContextFilter(correlation_id, user_id)
    logger.addFilter(context_filter)


def log_error(error_type: str, message: str, details: Dict[str, Any] = None, 
              location: str = None, user_id: str = None, request_id: str = None):
    """Log comprehensive error information with context."""
    logger = get_logger('vessel_guard.error')
    
    error_context = {
        'error_type': error_type,
        'error_event': True,
        'timestamp': datetime.utcnow().isoformat() + 'Z',
        'severity': 'ERROR'
    }
    
    # Add location information
    if location:
        error_context['location'] = location
    
    # Add user context
    if user_id:
        error_context['user_id'] = user_id
    
    # Add request context
    if request_id:
        error_context['request_id'] = request_id
    
    # Add error details
    if details:
        error_context.update(details)
    
    logger.error(f"Error occurred: {error_type} - {message}", extra=error_context)


def log_exception(exception: Exception, context: Dict[str, Any] = None, 
                  location: str = None, user_id: str = None, request_id: str = None):
    """Log exception with full traceback and context."""
    logger = get_logger('vessel_guard.exception')
    
    exception_context = {
        'exception_type': type(exception).__name__,
        'exception_message': str(exception),
        'error_event': True,
        'timestamp': datetime.utcnow().isoformat() + 'Z',
        'severity': 'ERROR'
    }
    
    # Add location information
    if location:
        exception_context['location'] = location
    
    # Add user context
    if user_id:
        exception_context['user_id'] = user_id
    
    # Add request context
    if request_id:
        exception_context['request_id'] = request_id
    
    # Add additional context
    if context:
        exception_context.update(context)
    
    logger.exception(f"Exception occurred: {type(exception).__name__}", extra=exception_context)


def log_database_error(operation: str, table: str, error: Exception, 
                      query: str = None, params: Dict[str, Any] = None):
    """Log database-specific errors with query context."""
    logger = get_logger('vessel_guard.database.error')
    
    db_error_context = {
        'error_type': 'database_error',
        'operation': operation,
        'table': table,
        'exception_type': type(error).__name__,
        'exception_message': str(error),
        'error_event': True,
        'database_operation': True,
        'timestamp': datetime.utcnow().isoformat() + 'Z'
    }
    
    # Add query information (sanitized)
    if query:
        db_error_context['query'] = query[:500]  # Truncate long queries
    
    # Add parameters (sanitized)
    if params:
        # Remove sensitive data from parameters
        safe_params = {k: v for k, v in params.items() 
                      if k.lower() not in ['password', 'token', 'secret']}
        db_error_context['params'] = safe_params
    
    logger.error(f"Database error in {operation} on {table}: {str(error)}", 
                extra=db_error_context)


def log_authentication_error(error_type: str, details: Dict[str, Any] = None,
                            ip_address: str = None, user_agent: str = None):
    """Log authentication and authorization errors."""
    logger = get_logger('vessel_guard.auth.error')
    
    auth_error_context = {
        'error_type': 'auth_error',
        'auth_error_type': error_type,
        'security_event': True,
        'error_event': True,
        'timestamp': datetime.utcnow().isoformat() + 'Z',
        'severity': 'WARNING'
    }
    
    # Add request context
    if ip_address:
        auth_error_context['ip_address'] = ip_address
    
    if user_agent:
        auth_error_context['user_agent'] = user_agent
    
    # Add error details
    if details:
        auth_error_context.update(details)
    
    logger.warning(f"Authentication error: {error_type}", extra=auth_error_context)


def log_critical_error(error_type: str, message: str, details: Dict[str, Any] = None,
                      location: str = None, requires_immediate_attention: bool = True):
    """Log critical errors that require immediate attention."""
    logger = get_logger('vessel_guard.critical')
    
    critical_context = {
        'error_type': error_type,
        'critical_error': True,
        'error_event': True,
        'requires_immediate_attention': requires_immediate_attention,
        'timestamp': datetime.utcnow().isoformat() + 'Z',
        'severity': 'CRITICAL'
    }
    
    # Add location information
    if location:
        critical_context['location'] = location
    
    # Add error details
    if details:
        critical_context.update(details)
    
    logger.critical(f"CRITICAL ERROR: {error_type} - {message}", extra=critical_context)


# Error tracking decorator
def track_errors(operation_name: str = None, log_args: bool = False):
    """Decorator to automatically track errors in functions."""
    def decorator(func):
        import functools
        
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            op_name = operation_name or f"{func.__module__}.{func.__name__}"
            
            try:
                return func(*args, **kwargs)
            except Exception as e:
                error_context = {
                    'function': func.__name__,
                    'function_module': func.__module__,
                    'operation': op_name
                }
                
                # Add arguments if requested (be careful with sensitive data)
                if log_args:
                    error_context['args_count'] = len(args)
                    error_context['kwargs_keys'] = list(kwargs.keys())
                
                log_exception(e, context=error_context, location=op_name)
                raise
        
        return wrapper
    return decorator


def create_error_summary_report(hours_back: int = 24) -> Dict[str, Any]:
    """Create a summary report of errors in the last N hours."""
    from datetime import datetime, timedelta
    
    cutoff_time = datetime.utcnow() - timedelta(hours=hours_back)
    
    # Query logs for error events
    logger = get_logger('vessel_guard.error')
    error_logs = logger.logger.handlers[0].baseFilename
    
    # Read and parse log file
    from collections import defaultdict
    import json
    
    error_summary = defaultdict(lambda: {'count': 0, 'last_seen': None, 'details': []})
    
    try:
        with open(error_logs, 'r', encoding='utf8') as f:
            for line in f:
                if '"error_event": true' in line:
                    try:
                        log_entry = json.loads(line)
                        
                        # Filter by time range
                        log_time = datetime.fromisoformat(log_entry['timestamp'].replace('Z', '+00:00'))
                        if log_time < cutoff_time:
                            continue
                        
                        error_type = log_entry.get('error_type', 'unknown')
                        error_summary[error_type]['count'] += 1
                        error_summary[error_type]['last_seen'] = log_time.isoformat()
                        error_summary[error_type]['details'].append(log_entry)
                    except Exception:
                        continue
    except Exception as e:
        logger.error(f"Failed to read error log file for report: {str(e)}")
    
    return {
        'from': cutoff_time.isoformat(),
        'to': datetime.utcnow().isoformat(),
        'error_count': sum(summary['count'] for summary in error_summary.values()),
        'errors': [
            {
                'type': error_type,
                'count': summary['count'],
                'last_seen': summary['last_seen'],
                'details': summary['details'][:5]  # Limit details
            }
            for error_type, summary in error_summary.items()
        ]
    }