"""
Project model for engineering project management.

Defines engineering projects that contain vessels, calculations,
and compliance documentation.
"""

import enum
from datetime import datetime
from typing import TYPE_CHECKING, List

from sqlalchemy import Boolean, Column, DateTime, Enum, ForeignKey, Integer, String, Text, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.base import Base

if TYPE_CHECKING:
    from app.db.models.user import User
    from app.db.models.organization import Organization
    from app.db.models.vessel import Vessel
    from app.db.models.calculation import Calculation


class ProjectStatus(str, enum.Enum):
    """Project status enumeration."""
    ACTIVE = "active"
    COMPLETED = "completed"
    ON_HOLD = "on_hold"
    CANCELLED = "cancelled"
    ARCHIVED = "archived"


class ProjectPriority(str, enum.Enum):
    """Project priority levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class Project(Base):
    """
    Project model for engineering project management.
    
    Contains vessels, calculations, and compliance documentation
    for engineering analysis projects.
    """
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    
    # Basic project information
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)
    project_number = Column(String(100), nullable=True, unique=True, index=True)
    
    # Client information
    client_name = Column(String(255), nullable=True)
    client_contact = Column(String(255), nullable=True)
    client_email = Column(String(255), nullable=True)
    client_phone = Column(String(20), nullable=True)
    
    # Project management
    status = Column(Enum(ProjectStatus), default=ProjectStatus.ACTIVE, nullable=False)
    priority = Column(Enum(ProjectPriority), default=ProjectPriority.MEDIUM, nullable=False)
    
    # Timeline
    start_date = Column(DateTime(timezone=True), nullable=True)
    target_completion_date = Column(DateTime(timezone=True), nullable=True)
    actual_completion_date = Column(DateTime(timezone=True), nullable=True)
    
    # Engineering standards and codes
    engineering_standards = Column(JSON, nullable=True)  # List of applicable standards
    design_codes = Column(JSON, nullable=True)  # List of design codes (ASME, API, etc.)
    
    # Location and environment
    location = Column(String(255), nullable=True)
    operating_environment = Column(String(100), nullable=True)  # indoor, outdoor, marine, etc.
    
    # Project settings
    default_units = Column(String(20), default="imperial", nullable=False)
    pressure_units = Column(String(10), default="psi", nullable=False)
    temperature_units = Column(String(10), default="fahrenheit", nullable=False)
    
    # Organization and ownership
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Project tags and categories
    tags = Column(JSON, nullable=True)  # Project tags for organization
    category = Column(String(100), nullable=True)  # petrochemical, power, manufacturing, etc.
    
    # Compliance and certification
    requires_certification = Column(Boolean, default=False, nullable=False)
    certification_body = Column(String(255), nullable=True)
    certification_requirements = Column(Text, nullable=True)
    
    # Audit fields
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    organization = relationship("Organization", back_populates="projects")
    owner = relationship("User", back_populates="owned_projects", foreign_keys=[owner_id])
    
    # Project contents
    vessels = relationship("Vessel", back_populates="project", cascade="all, delete-orphan")
    calculations = relationship("Calculation", back_populates="project", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<Project(id={self.id}, name='{self.name}', status='{self.status}')>"

    @property
    def is_active(self) -> bool:
        """Check if project is currently active."""
        return self.status == ProjectStatus.ACTIVE

    @property
    def is_completed(self) -> bool:
        """Check if project is completed."""
        return self.status == ProjectStatus.COMPLETED

    @property
    def is_overdue(self) -> bool:
        """Check if project is overdue."""
        if not self.target_completion_date or self.is_completed:
            return False
        return datetime.utcnow() > self.target_completion_date

    @property
    def vessel_count(self) -> int:
        """Get number of vessels in project."""
        return len(self.vessels) if self.vessels else 0

    @property
    def calculation_count(self) -> int:
        """Get number of calculations in project."""
        return len(self.calculations) if self.calculations else 0

    @property
    def progress_percentage(self) -> float:
        """Calculate project progress percentage."""
        if not self.start_date or not self.target_completion_date:
            return 0.0
        
        total_duration = (self.target_completion_date - self.start_date).total_seconds()
        if total_duration <= 0:
            return 100.0
        
        if self.is_completed and self.actual_completion_date:
            return 100.0
        
        elapsed_duration = (datetime.utcnow() - self.start_date).total_seconds()
        progress = min(100.0, max(0.0, (elapsed_duration / total_duration) * 100))
        
        return round(progress, 1)
