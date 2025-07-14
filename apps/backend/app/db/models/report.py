"""
Report model for generated calculation and inspection reports.

Defines report metadata, generation tracking, and storage
for PDF reports and documentation.
"""

import enum
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, Column, DateTime, Enum, ForeignKey, Integer, String, Text, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.base import Base

if TYPE_CHECKING:
    from app.db.models.user import User
    from app.db.models.project import Project
    from app.db.models.calculation import Calculation
    from app.db.models.inspection import Inspection


class ReportType(str, enum.Enum):
    """Report type enumeration."""
    CALCULATION = "calculation"
    INSPECTION = "inspection"
    PROJECT_SUMMARY = "project_summary"
    COMPLIANCE = "compliance"
    CUSTOM = "custom"


class ReportFormat(str, enum.Enum):
    """Report format enumeration."""
    PDF = "pdf"
    DOCX = "docx"
    HTML = "html"
    CSV = "csv"
    EXCEL = "excel"


class ReportStatus(str, enum.Enum):
    """Report generation status."""
    PENDING = "pending"
    GENERATING = "generating"
    COMPLETED = "completed"
    FAILED = "failed"
    EXPIRED = "expired"


class Report(Base):
    """
    Report model for generated documents and analysis reports.
    
    Tracks report generation, storage, and access for
    calculation results and inspection documentation.
    """
    __tablename__ = "reports"

    id = Column(Integer, primary_key=True, index=True)
    
    # Basic identification
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    report_type = Column(Enum(ReportType), nullable=False)
    report_format = Column(Enum(ReportFormat), default=ReportFormat.PDF, nullable=False)
    
    # Generation tracking
    status = Column(Enum(ReportStatus), default=ReportStatus.PENDING, nullable=False)
    generated_at = Column(DateTime(timezone=True), nullable=True)
    generation_time_seconds = Column(Integer, nullable=True)
    error_message = Column(Text, nullable=True)
    
    # File information
    file_path = Column(String(500), nullable=True)
    file_size_bytes = Column(Integer, nullable=True)
    file_hash = Column(String(128), nullable=True)  # SHA-256 hash for integrity
    
    # Content and metadata
    template_name = Column(String(100), nullable=True)
    template_version = Column(String(20), nullable=True)
    report_parameters = Column(JSON, nullable=True)  # Parameters used for generation
    
    # Access and security
    is_public = Column(Boolean, default=False, nullable=False)
    access_level = Column(String(20), default="organization", nullable=False)  # public, organization, project, private
    download_count = Column(Integer, default=0, nullable=False)
    
    # Expiration and retention
    expires_at = Column(DateTime(timezone=True), nullable=True)
    retention_period_days = Column(Integer, nullable=True)
    auto_delete = Column(Boolean, default=False, nullable=False)
    
    # Content summary
    page_count = Column(Integer, nullable=True)
    sections = Column(JSON, nullable=True)  # List of report sections
    summary = Column(Text, nullable=True)
    
    # Relationships
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=True)
    calculation_id = Column(Integer, ForeignKey("calculations.id"), nullable=True)
    inspection_id = Column(Integer, ForeignKey("inspections.id"), nullable=True)
    generated_by_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Version control
    version = Column(String(20), default="1.0", nullable=False)
    previous_version_id = Column(Integer, ForeignKey("reports.id"), nullable=True)
    
    # Digital signature and certification
    is_certified = Column(Boolean, default=False, nullable=False)
    certified_by_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    certified_at = Column(DateTime(timezone=True), nullable=True)
    digital_signature = Column(Text, nullable=True)
    
    # Audit fields
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    project = relationship("Project", foreign_keys=[project_id])
    calculation = relationship("Calculation", foreign_keys=[calculation_id])
    inspection = relationship("Inspection", foreign_keys=[inspection_id])
    generated_by = relationship("User", foreign_keys=[generated_by_id])
    certified_by = relationship("User", foreign_keys=[certified_by_id])
    previous_version = relationship("Report", remote_side=[id])

    def __repr__(self) -> str:
        return f"<Report(id={self.id}, title='{self.title}', type='{self.report_type}')>"

    @property
    def is_generated(self) -> bool:
        """Check if report is successfully generated."""
        return self.status == ReportStatus.COMPLETED

    @property
    def is_expired(self) -> bool:
        """Check if report has expired."""
        if not self.expires_at:
            return False
        return datetime.utcnow() > self.expires_at

    @property
    def is_downloadable(self) -> bool:
        """Check if report is available for download."""
        return self.is_generated and not self.is_expired and self.file_path

    @property
    def file_size_mb(self) -> float:
        """Get file size in megabytes."""
        if not self.file_size_bytes:
            return 0.0
        return self.file_size_bytes / (1024 * 1024)

    @property
    def age_days(self) -> int:
        """Get report age in days."""
        if not self.generated_at:
            return 0
        delta = datetime.utcnow() - self.generated_at
        return delta.days

    def increment_download_count(self) -> None:
        """Increment download counter."""
        self.download_count += 1

    def is_accessible_by_user(self, user_id: int, user_organization_id: int) -> bool:
        """
        Check if report is accessible by given user.
        
        Args:
            user_id: User ID requesting access
            user_organization_id: User's organization ID
            
        Returns:
            True if accessible, False otherwise
        """
        # Public reports are accessible to all
        if self.is_public and self.access_level == "public":
            return True
        
        # Private reports only accessible to generator
        if self.access_level == "private":
            return user_id == self.generated_by_id
        
        # Organization level reports
        if self.access_level == "organization":
            # Need to check if user belongs to same organization as project
            if self.project_id:
                # This would need to be implemented with proper joins
                # For now, assume same organization if user_organization_id matches
                return True  # Simplified for now
        
        # Project level reports - check if user has access to project
        if self.access_level == "project":
            # This would need project membership check
            return True  # Simplified for now
        
        return False

    def should_auto_delete(self) -> bool:
        """Check if report should be automatically deleted."""
        if not self.auto_delete or not self.retention_period_days:
            return False
        
        if not self.generated_at:
            return False
        
        retention_end = self.generated_at + datetime.timedelta(days=self.retention_period_days)
        return datetime.utcnow() > retention_end
