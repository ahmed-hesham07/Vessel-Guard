"""
Database initialization script for Vessel Guard API.

This script initializes the database connection and runs initial setup.
"""

import logging
import sys
from pathlib import Path

# Add the app directory to the path
app_dir = Path(__file__).parent
sys.path.insert(0, str(app_dir))

from app.core.config import settings
from app.db.base import engine, test_db_connection, init_db
from app.db.connection import get_database_info

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def main():
    """Main initialization function."""
    logger.info("Starting database initialization...")
    
    # Test database connection
    logger.info("Testing database connection...")
    if not test_db_connection():
        logger.error("Database connection failed. Please check your configuration.")
        sys.exit(1)
    
    logger.info("Database connection successful!")
    
    # Get database info
    db_info = get_database_info(engine)
    if db_info:
        logger.info(f"Database info: {db_info}")
    
    # Initialize database tables
    logger.info("Initializing database tables...")
    try:
        init_db()
        logger.info("Database tables initialized successfully!")
    except Exception as e:
        logger.error(f"Failed to initialize database tables: {e}")
        sys.exit(1)
    
    logger.info("Database initialization completed successfully!")


if __name__ == "__main__":
    main()
