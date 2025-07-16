#!/usr/bin/env python3
"""
Test script for the error logging system.

Tests various error scenarios to ensure proper logging.
"""

import asyncio
import time
from datetime import datetime

# Add the app directory to Python path
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from app.core.logging_config import (
    setup_logging, log_error, log_exception, log_database_error,
    log_authentication_error, log_critical_error, get_logger
)
from app.utils.error_tracking import (
    ErrorTracker, track_operation, log_user_error, 
    log_business_logic_error, log_security_incident
)


def test_basic_logging():
    """Test basic logging functionality."""
    print("Testing basic logging...")
    
    logger = get_logger('test')
    
    # Test different log levels
    logger.info("This is an info message")
    logger.warning("This is a warning message")
    logger.error("This is an error message")
    
    print("✓ Basic logging test completed")


def test_error_logging():
    """Test error logging functions."""
    print("Testing error logging functions...")
    
    # Test basic error logging
    log_error(
        error_type='test_error',
        message='This is a test error',
        details={
            'test_field': 'test_value',
            'error_code': 'TEST_001'
        },
        location='test_basic_logging'
    )
    
    # Test exception logging
    try:
        raise ValueError("This is a test exception")
    except Exception as e:
        log_exception(
            exception=e,
            context={'test_context': 'exception_test'},
            location='test_error_logging'
        )
    
    # Test database error logging
    try:
        raise Exception("Database connection failed")
    except Exception as e:
        log_database_error(
            operation='SELECT',
            table='users',
            error=e,
            query='SELECT * FROM users WHERE id = ?',
            params={'id': 123}
        )
    
    # Test authentication error logging
    log_authentication_error(
        error_type='invalid_credentials',
        details={
            'username': 'test_user',
            'attempt_count': 3
        },
        ip_address='192.168.1.100',
        user_agent='Mozilla/5.0 Test Browser'
    )
    
    # Test critical error logging
    log_critical_error(
        error_type='system_failure',
        message='Critical system component failed',
        details={
            'component': 'database',
            'error_code': 'CRIT_001'
        },
        location='system_startup'
    )
    
    print("✓ Error logging functions test completed")


def test_error_tracking():
    """Test error tracking utilities."""
    print("Testing error tracking utilities...")
    
    # Test error tracker context manager
    with ErrorTracker('test_operation', {'user_id': 'test_user'}) as tracker:
        tracker.log_error('operation_error', 'Something went wrong in operation')
    
    # Test track_operation context manager
    with track_operation('test_track_operation', {'test_module': 'test'}) as tracker:
        # Simulate some work
        time.sleep(0.1)
        tracker.log_error('tracked_error', 'Error in tracked operation')
    
    # Test user error logging
    log_user_error(
        user_id='user123',
        error_type='validation_error',
        details={
            'field': 'email',
            'value': 'invalid-email',
            'rule': 'email_format'
        }
    )
    
    # Test business logic error logging
    log_business_logic_error(
        operation='calculate_pressure',
        entity='pressure_vessel',
        details={
            'vessel_id': 'pv001',
            'calculation_type': 'stress_analysis',
            'error_reason': 'insufficient_material_data'
        }
    )
    
    # Test security incident logging
    log_security_incident(
        incident_type='unauthorized_access_attempt',
        details={
            'ip_address': '192.168.1.200',
            'user_agent': 'Suspicious Bot',
            'endpoint': '/api/v1/admin/users',
            'method': 'POST'
        },
        severity='HIGH'
    )
    
    print("✓ Error tracking utilities test completed")


def test_exception_handling():
    """Test exception handling in different scenarios."""
    print("Testing exception handling...")
    
    # Test various exception types
    exceptions_to_test = [
        ValueError("Invalid value provided"),
        KeyError("Required key not found"),
        TypeError("Type mismatch error"),
        AttributeError("Attribute not found"),
        RuntimeError("Runtime error occurred")
    ]
    
    for i, exception in enumerate(exceptions_to_test):
        try:
            raise exception
        except Exception as e:
            log_exception(
                exception=e,
                context={
                    'test_number': i + 1,
                    'exception_name': type(e).__name__
                },
                location='test_exception_handling'
            )
    
    print("✓ Exception handling test completed")


def test_performance_logging():
    """Test performance-related logging."""
    print("Testing performance logging...")
    
    from app.core.logging_config import log_performance
    
    # Simulate some operations with performance logging
    operations = [
        ('database_query', 150.5),
        ('api_request', 45.2),
        ('calculation', 890.7),
        ('file_upload', 2340.1)
    ]
    
    for operation, duration in operations:
        log_performance(
            func_name=operation,
            duration_ms=duration,
            operation_type='test',
            test_run=True
        )
    
    print("✓ Performance logging test completed")


def test_structured_logging():
    """Test structured logging with context."""
    print("Testing structured logging...")
    
    logger = get_logger('test.structured')
    
    # Test with various contexts
    logger.info(
        "User logged in",
        extra={
            'user_id': 'user123',
            'session_id': 'session456',
            'ip_address': '192.168.1.50',
            'user_agent': 'Chrome/91.0',
            'login_method': 'password'
        }
    )
    
    logger.warning(
        "Rate limit exceeded",
        extra={
            'user_id': 'user789',
            'ip_address': '192.168.1.100',
            'requests_per_minute': 120,
            'limit': 100,
            'endpoint': '/api/v1/calculations'
        }
    )
    
    logger.error(
        "Payment processing failed",
        extra={
            'user_id': 'user456',
            'transaction_id': 'txn_abc123',
            'amount': 99.99,
            'currency': 'USD',
            'payment_method': 'credit_card',
            'error_code': 'PAYMENT_DECLINED'
        }
    )
    
    print("✓ Structured logging test completed")


async def test_async_logging():
    """Test logging in async context."""
    print("Testing async logging...")
    
    logger = get_logger('test.async')
    
    async def async_operation():
        logger.info("Starting async operation")
        await asyncio.sleep(0.1)  # Simulate async work
        
        try:
            # Simulate an error
            raise Exception("Async operation failed")
        except Exception as e:
            log_exception(
                exception=e,
                context={'async_operation': True},
                location='async_operation'
            )
    
    await async_operation()
    
    print("✓ Async logging test completed")


def test_log_file_creation():
    """Test that log files are created properly."""
    print("Testing log file creation...")
    
    from pathlib import Path
    
    log_dir = Path('logs')
    expected_files = [
        'vessel_guard.log',
        'errors.log',
        'security.log',
        'api_access.log',
        'database.log'
    ]
    
    created_files = []
    missing_files = []
    
    for file_name in expected_files:
        file_path = log_dir / file_name
        if file_path.exists():
            created_files.append(file_name)
        else:
            missing_files.append(file_name)
    
    print(f"✓ Created files: {created_files}")
    if missing_files:
        print(f"⚠ Missing files: {missing_files}")
    
    print("✓ Log file creation test completed")


def main():
    """Run all tests."""
    print("=" * 60)
    print("VESSEL GUARD ERROR LOGGING SYSTEM TEST")
    print("=" * 60)
    print(f"Started at: {datetime.now()}")
    print()
    
    # Setup logging
    setup_logging()
    
    # Run tests
    test_basic_logging()
    print()
    
    test_error_logging()
    print()
    
    test_error_tracking()
    print()
    
    test_exception_handling()
    print()
    
    test_performance_logging()
    print()
    
    test_structured_logging()
    print()
    
    # Run async test
    asyncio.run(test_async_logging())
    print()
    
    test_log_file_creation()
    print()
    
    print("=" * 60)
    print("ALL TESTS COMPLETED")
    print("=" * 60)
    print(f"Completed at: {datetime.now()}")
    print()
    print("Check the logs/ directory for generated log files:")
    print("- vessel_guard.log (main application log)")
    print("- errors.log (error-specific log)")
    print("- security.log (security events)")
    print("- api_access.log (API access logs)")
    print("- database.log (database operations)")


if __name__ == "__main__":
    main()
