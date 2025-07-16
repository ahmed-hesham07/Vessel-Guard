"""
Database connection utilities for Vessel Guard API.

This module provides utilities for managing database connections,
including connection pooling and health checks.
"""

import logging
from typing import Optional
from contextlib import contextmanager
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool
from sqlalchemy.exc import SQLAlchemyError

from app.core.config import settings

logger = logging.getLogger(__name__)


class DatabaseManager:
    """Database connection manager with connection pooling."""
    
    def __init__(self):
        self.engine = None
        self._initialize_engine()
    
    def _initialize_engine(self):
        """Initialize the database engine with appropriate settings."""
        try:
            if settings.TESTING:
                # Use SQLite for testing
                database_url = "sqlite:///./test.db"
                self.engine = create_engine(
                    database_url,
                    connect_args={"check_same_thread": False},
                    poolclass=StaticPool,
                    echo=settings.DEBUG,
                )
            else:
                # Use PostgreSQL for production/development
                database_url = str(settings.DATABASE_URL)
                
                # Configure connection pool for production
                pool_settings = {
                    "pool_pre_ping": True,
                    "pool_recycle": 300,  # 5 minutes
                    "pool_size": 10,
                    "max_overflow": 20,
                    "echo": settings.DEBUG,
                }
                
                # For Fly.io, adjust pool settings for better performance
                if "flycast" in database_url or "fly.dev" in database_url:
                    pool_settings.update({
                        "pool_size": 5,
                        "max_overflow": 10,
                        "pool_timeout": 30,
                        "pool_recycle": 1800,  # 30 minutes
                    })
                
                self.engine = create_engine(database_url, **pool_settings)
            
            logger.info("Database engine initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize database engine: {e}")
            raise
    
    def get_engine(self):
        """Get the database engine."""
        return self.engine
    
    def test_connection(self) -> bool:
        """Test database connection."""
        try:
            with self.engine.connect() as connection:
                result = connection.execute(text("SELECT 1"))
                result.fetchone()
            logger.info("Database connection test successful")
            return True
        except SQLAlchemyError as e:
            logger.error(f"Database connection test failed: {e}")
            return False
    
    def get_connection_info(self) -> dict:
        """Get database connection information."""
        try:
            with self.engine.connect() as connection:
                # Get database version
                if "postgresql" in str(self.engine.url):
                    version_result = connection.execute(text("SELECT version()"))
                    version = version_result.fetchone()[0]
                    
                    # Get database name
                    db_result = connection.execute(text("SELECT current_database()"))
                    database = db_result.fetchone()[0]
                    
                    return {
                        "database_type": "PostgreSQL",
                        "version": version,
                        "database": database,
                        "host": self.engine.url.host,
                        "port": self.engine.url.port,
                    }
                else:
                    return {
                        "database_type": "SQLite",
                        "database": str(self.engine.url.database),
                    }
        except Exception as e:
            logger.error(f"Failed to get connection info: {e}")
            return {"error": str(e)}
    
    @contextmanager
    def get_session(self):
        """Context manager for database sessions."""
        session = Session(bind=self.engine)
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error(f"Database session error: {e}")
            raise
        finally:
            session.close()
    
    def close(self):
        """Close the database engine."""
        if self.engine:
            self.engine.dispose()
            logger.info("Database engine closed")


# Global database manager instance
db_manager = DatabaseManager()

# Convenience function for getting the engine
def get_engine():
    """Get the database engine."""
    return db_manager.get_engine()

# Convenience function for testing connection
def test_db_connection() -> bool:
    """Test database connection."""
    return db_manager.test_connection()

# Convenience function for getting connection info
def get_db_info() -> dict:
    """Get database connection information."""
    return db_manager.get_connection_info()
