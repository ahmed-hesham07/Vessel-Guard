#!/usr/bin/env python3
"""
Test script to verify Aiven PostgreSQL integration.

This script tests all aspects of the database integration:
- Connection to Aiven PostgreSQL
- SSL certificate validation
- Database operations
- Model creation
"""

import sys
import os
import logging
from pathlib import Path

# Add the app directory to the path
app_dir = Path(__file__).parent
sys.path.insert(0, str(app_dir))

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_imports():
    """Test that all modules can be imported."""
    logger.info("Testing imports...")
    
    try:
        from app.core.config import settings
        logger.info("✓ Settings imported successfully")
        
        from app.db.base import engine, Base
        logger.info("✓ Database base imported successfully")
        
        from app.db.connection import test_database_connection, get_database_info
        logger.info("✓ Database connection utilities imported successfully")
        
        # Test model imports
        from app.db.models import User, Organization, Project, Vessel
        logger.info("✓ Models imported successfully")
        
        return True
        
    except Exception as e:
        logger.error(f"✗ Import failed: {e}")
        return False

def test_database_connection():
    """Test database connection."""
    logger.info("Testing database connection...")
    
    try:
        from app.db.base import test_db_connection
        
        if test_db_connection():
            logger.info("✓ Database connection successful")
            return True
        else:
            logger.error("✗ Database connection failed")
            return False
            
    except Exception as e:
        logger.error(f"✗ Database connection error: {e}")
        return False

def test_ssl_configuration():
    """Test SSL configuration."""
    logger.info("Testing SSL configuration...")
    
    try:
        from app.core.config import settings
        
        if settings.POSTGRES_SSL_MODE == "require":
            logger.info("✓ SSL mode is set to 'require'")
        else:
            logger.warning(f"⚠ SSL mode is set to '{settings.POSTGRES_SSL_MODE}'")
            
        if settings.POSTGRES_SSL_CERT_PATH:
            cert_path = settings.POSTGRES_SSL_CERT_PATH
            if os.path.exists(cert_path):
                logger.info(f"✓ SSL certificate found at {cert_path}")
                return True
            else:
                logger.error(f"✗ SSL certificate not found at {cert_path}")
                return False
        else:
            logger.warning("⚠ No SSL certificate path configured")
            return True
            
    except Exception as e:
        logger.error(f"✗ SSL configuration error: {e}")
        return False

def test_database_info():
    """Test database information retrieval."""
    logger.info("Testing database information...")
    
    try:
        from app.db.base import engine
        from app.db.connection import get_database_info
        
        info = get_database_info(engine)
        
        if info:
            logger.info("✓ Database information retrieved successfully:")
            for key, value in info.items():
                logger.info(f"  {key}: {value}")
            return True
        else:
            logger.error("✗ Failed to retrieve database information")
            return False
            
    except Exception as e:
        logger.error(f"✗ Database info error: {e}")
        return False

def test_model_creation():
    """Test model creation."""
    logger.info("Testing model creation...")
    
    try:
        from app.db.base import Base, engine
        
        # Create tables
        Base.metadata.create_all(bind=engine)
        logger.info("✓ Models created successfully")
        
        # Check if tables exist
        from sqlalchemy import inspect
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        
        if tables:
            logger.info(f"✓ Found {len(tables)} tables: {', '.join(tables)}")
            return True
        else:
            logger.warning("⚠ No tables found in database")
            return False
            
    except Exception as e:
        logger.error(f"✗ Model creation error: {e}")
        return False

def main():
    """Run all tests."""
    logger.info("=== Aiven PostgreSQL Integration Test ===")
    
    tests = [
        ("Imports", test_imports),
        ("Database Connection", test_database_connection),
        ("SSL Configuration", test_ssl_configuration),
        ("Database Information", test_database_info),
        ("Model Creation", test_model_creation),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        logger.info(f"\n--- {test_name} ---")
        result = test_func()
        results.append((test_name, result))
    
    # Summary
    logger.info("\n=== Test Summary ===")
    passed = 0
    for test_name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        logger.info(f"{test_name}: {status}")
        if result:
            passed += 1
    
    logger.info(f"\nPassed: {passed}/{len(results)} tests")
    
    if passed == len(results):
        logger.info("🎉 All tests passed! Aiven integration is working correctly.")
        return 0
    else:
        logger.error("❌ Some tests failed. Please check the configuration.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
