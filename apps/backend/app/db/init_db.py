"""
Database initialization and seeding utilities.

Handles database setup, initial data seeding, and development data.
"""

import asyncio
import logging
from typing import Optional

from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import get_password_hash
from app.db.base import SessionLocal, init_db as create_tables
from app.db.models.user import User, UserRole
from app.db.models.organization import Organization

logger = logging.getLogger(__name__)


async def init_db() -> None:
    """
    Initialize database with tables and initial data.
    """
    try:
        # Create all tables
        create_tables()
        
        # Create initial data
        db = SessionLocal()
        try:
            await create_initial_data(db)
        finally:
            db.close()
            
        logger.info("Database initialization completed successfully")
        
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        raise


async def create_initial_data(db: Session) -> None:
    """
    Create initial application data.
    
    Args:
        db: Database session
    """
    # Create default organization if none exists
    org = db.query(Organization).first()
    if not org:
        default_org = Organization(
            name="Default Organization",
            description="Default organization for Vessel Guard",
            subscription_type="trial",
            is_active=True
        )
        db.add(default_org)
        db.commit()
        db.refresh(default_org)
        logger.info("Created default organization")
    else:
        default_org = org
    
    # Create admin user if none exists
    admin_user = db.query(User).filter(User.email == "admin@vesselguard.com").first()
    if not admin_user:
        admin_user = User(
            email="admin@vesselguard.com",
            hashed_password=get_password_hash("admin123!"),
            first_name="System",
            last_name="Administrator",
            role=UserRole.ADMIN,
            is_active=True,
            is_verified=True,
            organization_id=default_org.id
        )
        db.add(admin_user)
        db.commit()
        db.refresh(admin_user)
        logger.info("Created admin user")


async def seed_initial_data() -> None:
    """
    Seed database with sample data for development.
    """
    if settings.TESTING:
        return
        
    db = SessionLocal()
    try:
        await create_sample_data(db)
    finally:
        db.close()


async def create_sample_data(db: Session) -> None:
    """
    Create sample data for development and testing.
    
    Args:
        db: Database session
    """
    # Check if sample data already exists
    user_count = db.query(User).count()
    if user_count > 1:  # More than just the admin user
        logger.info("Sample data already exists, skipping creation")
        return
    
    # Get default organization
    default_org = db.query(Organization).first()
    if not default_org:
        logger.error("Default organization not found")
        return
    
    # Create sample users
    sample_users = [
        {
            "email": "engineer@vesselguard.com",
            "password": "engineer123!",
            "first_name": "John",
            "last_name": "Engineer",
            "role": UserRole.ENGINEER
        },
        {
            "email": "inspector@vesselguard.com", 
            "password": "inspector123!",
            "first_name": "Jane",
            "last_name": "Inspector",
            "role": UserRole.INSPECTOR
        },
        {
            "email": "manager@vesselguard.com",
            "password": "manager123!",
            "first_name": "Bob",
            "last_name": "Manager", 
            "role": UserRole.MANAGER
        }
    ]
    
    for user_data in sample_users:
        existing_user = db.query(User).filter(User.email == user_data["email"]).first()
        if not existing_user:
            user = User(
                email=user_data["email"],
                hashed_password=get_password_hash(user_data["password"]),
                first_name=user_data["first_name"],
                last_name=user_data["last_name"],
                role=user_data["role"],
                is_active=True,
                is_verified=True,
                organization_id=default_org.id
            )
            db.add(user)
    
    db.commit()
    logger.info("Sample data created successfully")


def reset_database() -> None:
    """
    Reset database by dropping and recreating all tables.
    WARNING: This will delete all data!
    """
    if not settings.DEBUG:
        raise RuntimeError("Database reset is only allowed in debug mode")
    
    from app.db.base import Base, engine
    
    logger.warning("Resetting database - all data will be lost!")
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    logger.info("Database reset completed")


if __name__ == "__main__":
    # Run initialization if called directly
    asyncio.run(init_db())
