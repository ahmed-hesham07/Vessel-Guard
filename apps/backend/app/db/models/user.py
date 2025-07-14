"""
User model for authentication and authorization.

Defines user entities with role-based access control
and organization membership.
"""

import enum
from datetime import datetime
from typing import TYPE_CHECKING, List

from sqlalchemy import Boolean, Column, DateTime, Enum, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.base import Base

if TYPE_CHECKING:
    from app.db.models.organization import Organization
    from app.db.models.project import Project
    from app.db.models.calculation import Calculation
    from app.db.models.inspection import Inspection


class UserRole(str, enum.Enum):
    """User roles for role-based access control."""
    ADMIN = "admin"
    MANAGER = "manager"
    ENGINEER = "engineer"
    INSPECTOR = "inspector"
    VIEWER = "viewer"


class User(Base):
    """
    User model for authentication and profile management.
    
    Stores user credentials, profile information, and
    organizational relationships.
    """
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    
    # Profile information
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    phone = Column(String(20), nullable=True)
    job_title = Column(String(100), nullable=True)
    department = Column(String(100), nullable=True)
    
    # Role and permissions
    role = Column(Enum(UserRole), nullable=False, default=UserRole.VIEWER)
    
    # Account status
    is_active = Column(Boolean, default=True, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)
    is_superuser = Column(Boolean, default=False, nullable=False)
    
    # Organization relationship
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False)
    
    # Authentication tracking
    last_login = Column(DateTime(timezone=True), nullable=True)
    failed_login_attempts = Column(Integer, default=0, nullable=False)
    locked_until = Column(DateTime(timezone=True), nullable=True)
    
    # Password reset
    password_reset_token = Column(String(255), nullable=True)
    password_reset_expires = Column(DateTime(timezone=True), nullable=True)
    
    # Email verification
    email_verification_token = Column(String(255), nullable=True)
    email_verification_expires = Column(DateTime(timezone=True), nullable=True)
    
    # Preferences
    timezone = Column(String(50), default="UTC", nullable=False)
    language = Column(String(10), default="en", nullable=False)
    
    # Audit fields
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    created_by_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    # Relationships
    organization = relationship("Organization", back_populates="users")
    created_by = relationship("User", remote_side=[id])
    
    # Projects (as owner or member)
    owned_projects = relationship("Project", back_populates="owner", foreign_keys="Project.owner_id")
    
    # Calculations performed by user
    calculations = relationship("Calculation", back_populates="calculated_by")
    
    # Inspections performed by user
    inspections = relationship("Inspection", back_populates="inspector")

    def __repr__(self) -> str:
        return f"<User(id={self.id}, email='{self.email}', role='{self.role}')>"

    @property
    def full_name(self) -> str:
        """Get user's full name."""
        return f"{self.first_name} {self.last_name}"

    @property
    def is_admin(self) -> bool:
        """Check if user has admin privileges."""
        return self.role == UserRole.ADMIN or self.is_superuser

    @property
    def is_manager(self) -> bool:
        """Check if user has manager privileges."""
        return self.role in [UserRole.ADMIN, UserRole.MANAGER] or self.is_superuser

    @property
    def can_create_projects(self) -> bool:
        """Check if user can create projects."""
        return self.role in [UserRole.ADMIN, UserRole.MANAGER, UserRole.ENGINEER]

    @property
    def can_perform_calculations(self) -> bool:
        """Check if user can perform engineering calculations."""
        return self.role in [UserRole.ADMIN, UserRole.MANAGER, UserRole.ENGINEER]

    @property
    def can_perform_inspections(self) -> bool:
        """Check if user can perform inspections."""
        return self.role in [UserRole.ADMIN, UserRole.MANAGER, UserRole.ENGINEER, UserRole.INSPECTOR]
