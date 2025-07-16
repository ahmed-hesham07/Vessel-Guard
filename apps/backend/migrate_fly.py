#!/usr/bin/env python3
"""
Database migration script for Fly.io deployment.

This script handles database initialization and migrations for the Vessel Guard API
when deployed on Fly.io.
"""

import os
import sys
import logging
from pathlib import Path

# Add the app directory to the Python path
sys.path.insert(0, str(Path(__file__).parent))

from app.core.config import settings
from app.db.connection import db_manager
from app.db.init_db import init_db

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def test_database_connection():
    """Test the database connection."""
    logger.info("Testing database connection...")
    
    try:
        if db_manager.test_connection():
            logger.info("Database connection successful!")
            
            # Get connection info
            db_info = db_manager.get_connection_info()
            logger.info(f"Database type: {db_info.get('database_type', 'unknown')}")
            logger.info(f"Database name: {db_info.get('database', 'unknown')}")
            
            if 'host' in db_info:
                logger.info(f"Database host: {db_info['host']}")
            
            return True
        else:
            logger.error("Database connection failed!")
            return False
    except Exception as e:
        logger.error(f"Database connection error: {e}")
        return False


def run_migrations():
    """Run database migrations."""
    logger.info("Running database migrations...")
    
    try:
        # Import alembic
        from alembic import command
        from alembic.config import Config
        
        # Set up alembic config
        alembic_cfg = Config("alembic.ini")
        alembic_cfg.set_main_option("sqlalchemy.url", str(settings.DATABASE_URL))
        
        # Run migrations
        command.upgrade(alembic_cfg, "head")
        logger.info("Database migrations completed successfully!")
        return True
    except Exception as e:
        logger.error(f"Migration failed: {e}")
        return False


def initialize_database():
    """Initialize the database."""
    logger.info("Initializing database...")
    
    try:
        # Run the init_db function
        init_db()
        logger.info("Database initialization completed successfully!")
        return True
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        return False


def main():
    """Main migration function."""
    logger.info("Starting database setup for Fly.io deployment...")
    
    # Test database connection
    if not test_database_connection():
        logger.error("Cannot proceed without database connection")
        sys.exit(1)
    
    # Run migrations if alembic is available
    if os.path.exists("alembic.ini"):
        if not run_migrations():
            logger.error("Migration failed, attempting database initialization...")
            if not initialize_database():
                logger.error("Database setup failed!")
                sys.exit(1)
    else:
        logger.info("No alembic.ini found, running database initialization...")
        if not initialize_database():
            logger.error("Database initialization failed!")
            sys.exit(1)
    
    logger.info("Database setup completed successfully!")


if __name__ == "__main__":
    main()
