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
    
    # Add file logging in production
    if is_production:
        config['handlers']['file'] = {
            'class': 'logging.handlers.RotatingFileHandler',
            'level': log_level,
            'formatter': 'json',
            'filename': log_dir / 'vessel_guard.log',
            'maxBytes': 10485760,  # 10MB
            'backupCount': 5,
            'encoding': 'utf8'
        }
        
        # Add file handler to all loggers
        for logger_config in config['loggers'].values():
            logger_config['handlers'].append('file')
        config['root']['handlers'].append('file')
    
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
