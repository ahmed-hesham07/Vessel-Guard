"""
Organization model for multi-tenancy support.

Defines organizations that users belong to and provides
subscription and billing management.
"""

import enum
from datetime import datetime
from typing import TYPE_CHECKING, List

from sqlalchemy import Boolean, Column, DateTime, Enum, Integer, String, Text, Numeric
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.base import Base

if TYPE_CHECKING:
    from app.db.models.user import User
    from app.db.models.project import Project


class SubscriptionType(str, enum.Enum):
    """Organization subscription types."""
    TRIAL = "trial"
    BASIC = "basic"
    PROFESSIONAL = "professional"
    ENTERPRISE = "enterprise"


class Organization(Base):
    """
    Organization model for multi-tenant architecture.
    
    Manages organization-level settings, subscriptions,
    and user memberships.
    """
    __tablename__ = "organizations"

    id = Column(Integer, primary_key=True, index=True)
    
    # Basic information
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)
    website = Column(String(255), nullable=True)
    
    # Contact information
    address_line1 = Column(String(255), nullable=True)
    address_line2 = Column(String(255), nullable=True)
    city = Column(String(100), nullable=True)
    state_province = Column(String(100), nullable=True)
    postal_code = Column(String(20), nullable=True)
    country = Column(String(100), nullable=True)
    
    phone = Column(String(20), nullable=True)
    email = Column(String(255), nullable=True)
    
    # Subscription and billing
    subscription_type = Column(Enum(SubscriptionType), default=SubscriptionType.TRIAL, nullable=False)
    subscription_starts_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    subscription_ends_at = Column(DateTime(timezone=True), nullable=True)
    
    # Limits based on subscription
    max_users = Column(Integer, default=5, nullable=False)
    max_projects = Column(Integer, default=10, nullable=False)
    max_calculations_per_month = Column(Integer, default=100, nullable=False)
    storage_limit_gb = Column(Numeric(10, 2), default=1.0, nullable=False)
    
    # Organization settings
    is_active = Column(Boolean, default=True, nullable=False)
    allow_user_registration = Column(Boolean, default=False, nullable=False)
    require_email_verification = Column(Boolean, default=True, nullable=False)
    
    # Industry and engineering settings
    primary_industry = Column(String(100), nullable=True)
    default_engineering_units = Column(String(20), default="imperial", nullable=False)  # imperial or metric
    default_pressure_units = Column(String(10), default="psi", nullable=False)
    default_temperature_units = Column(String(10), default="fahrenheit", nullable=False)
    
    # Audit fields
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    users = relationship("User", back_populates="organization")
    projects = relationship("Project", back_populates="organization")

    def __repr__(self) -> str:
        return f"<Organization(id={self.id}, name='{self.name}', subscription='{self.subscription_type}')>"

    @property
    def is_trial(self) -> bool:
        """Check if organization is on trial subscription."""
        return self.subscription_type == SubscriptionType.TRIAL

    @property
    def is_enterprise(self) -> bool:
        """Check if organization has enterprise subscription."""
        return self.subscription_type == SubscriptionType.ENTERPRISE

    @property
    def subscription_active(self) -> bool:
        """Check if subscription is currently active."""
        if not self.is_active:
            return False
        
        if self.subscription_ends_at is None:
            return True  # No end date means active
            
        return datetime.utcnow() < self.subscription_ends_at

    def can_add_user(self) -> bool:
        """Check if organization can add more users."""
        if not self.subscription_active:
            return False
        
        current_user_count = len(self.users) if self.users else 0
        return current_user_count < self.max_users

    def can_create_project(self) -> bool:
        """Check if organization can create more projects."""
        if not self.subscription_active:
            return False
        
        current_project_count = len(self.projects) if self.projects else 0
        return current_project_count < self.max_projects
