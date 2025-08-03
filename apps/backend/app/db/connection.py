"""
Database connection management for Vessel Guard API.

This module provides database connection utilities and health checks
specifically configured for PostgreSQL with SSL support.
"""

import logging
import os
from typing import Dict, Any
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from sqlalchemy.exc import SQLAlchemyError

from app.core.config import settings

logger = logging.getLogger(__name__)


def get_database_connection_params() -> Dict[str, Any]:
    """
    Get optimized database connection parameters for PostgreSQL with SSL support.
    
    Returns:
        Dictionary of connection parameters
    """
    params = {
        "pool_pre_ping": True,
        "pool_recycle": 300,  # Recycle connections every 5 minutes
        "pool_size": 15,      # Increased pool size for better performance
        "max_overflow": 30,   # Allow more overflow connections
        "pool_timeout": 30,   # Timeout for getting connection from pool
        "echo": settings.DEBUG,
        "echo_pool": settings.DEBUG,  # Echo pool events in debug mode
        
        # Performance optimizations
        "connect_args": {
            "options": "-c default_transaction_isolation=read_committed",
            "application_name": "vessel_guard_api",
            "connect_timeout": 10,
        }
    }
    
    # Add SSL configuration if using Aiven or other secure PostgreSQL
    if settings.POSTGRES_SSL_MODE and settings.POSTGRES_SSL_MODE != "disable":
        # Merge SSL configuration with existing connect_args
        ssl_context = {
            "sslmode": settings.POSTGRES_SSL_MODE,
        }
        
        if settings.POSTGRES_SSL_CERT_PATH and os.path.exists(settings.POSTGRES_SSL_CERT_PATH):
            ssl_context["sslrootcert"] = settings.POSTGRES_SSL_CERT_PATH
        
        # Merge with existing connect_args
        params["connect_args"].update(ssl_context)
    
    return params


def create_database_engine() -> Engine:
    """
    Create database engine with appropriate configuration.
    
    Returns:
        SQLAlchemy engine instance
    """
    connection_params = get_database_connection_params()
    
    try:
        engine = create_engine(
            str(settings.DATABASE_URL),
            **connection_params
        )
        
        # Test the connection
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
            
        logger.info("Database engine created successfully")
        return engine
        
    except SQLAlchemyError as e:
        logger.error(f"Failed to create database engine: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error creating database engine: {e}")
        raise


def test_database_connection(engine: Engine) -> bool:
    """
    Test database connection and basic functionality.
    
    Args:
        engine: SQLAlchemy engine instance
        
    Returns:
        True if connection is successful, False otherwise
    """
    try:
        with engine.connect() as conn:
            # Test basic connection
            result = conn.execute(text("SELECT 1 as test"))
            test_value = result.scalar()
            
            if test_value != 1:
                logger.error("Database connection test failed: unexpected result")
                return False
                
            # Test current database info - handle different database types
            try:
                if engine.dialect.name == 'postgresql':
                    result = conn.execute(text("SELECT current_database(), current_user"))
                    db_info = result.fetchone()
                    if db_info:
                        logger.info(f"Connected to PostgreSQL database: {db_info[0]} as user: {db_info[1]}")
                elif engine.dialect.name == 'sqlite':
                    # For SQLite, just check that we can execute a simple query
                    result = conn.execute(text("SELECT sqlite_version()"))
                    version = result.scalar()
                    logger.info(f"Connected to SQLite database, version: {version}")
                else:
                    logger.info(f"Connected to {engine.dialect.name} database")
            except Exception as e:
                # If database-specific info fails, that's okay as long as basic connection works
                logger.warning(f"Could not get database info: {e}")
            
            return True
            
    except SQLAlchemyError as e:
        logger.error(f"Database connection test failed: {e}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error during connection test: {e}")
        return False


def get_database_info(engine: Engine) -> Dict[str, Any]:
    """
    Get database information and connection details.
    
    Args:
        engine: SQLAlchemy engine instance
        
    Returns:
        Dictionary containing database information
    """
    try:
        with engine.connect() as conn:
            # Get database version and info
            queries = {
                "version": "SELECT version()",
                "current_database": "SELECT current_database()",
                "current_user": "SELECT current_user",
                "session_user": "SELECT session_user",
                "connection_count": "SELECT count(*) FROM pg_stat_activity WHERE datname = current_database()",
            }
            
            info = {}
            for key, query in queries.items():
                try:
                    result = conn.execute(text(query))
                    info[key] = result.scalar()
                except SQLAlchemyError as e:
                    logger.warning(f"Failed to execute query '{key}': {e}")
                    info[key] = None
                    
            return info
            
    except SQLAlchemyError as e:
        logger.error(f"Failed to get database info: {e}")
        return {}
    except Exception as e:
        logger.error(f"Unexpected error getting database info: {e}")
        return {}
