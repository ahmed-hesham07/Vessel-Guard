"""
Inspection model for vessel inspection records and findings.

Defines inspection records, findings, and compliance tracking
for pressure vessels and piping systems.
"""

import enum
from datetime import datetime
from typing import TYPE_CHECKING, List

from sqlalchemy import Boolean, Column, DateTime, Enum, ForeignKey, Integer, String, Text, Numeric, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.base import Base

if TYPE_CHECKING:
    from app.db.models.user import User
    from app.db.models.vessel import Vessel


class InspectionType(str, enum.Enum):
    """Inspection type enumeration."""
    INITIAL = "initial"
    PERIODIC = "periodic"
    SPECIAL = "special"
    EMERGENCY = "emergency"
    POST_REPAIR = "post_repair"
    PRE_SERVICE = "pre_service"
    SHUTDOWN = "shutdown"


class InspectionMethod(str, enum.Enum):
    """Inspection method enumeration."""
    VISUAL = "visual"
    ULTRASONIC = "ultrasonic"
    RADIOGRAPHIC = "radiographic"
    MAGNETIC_PARTICLE = "magnetic_particle"
    LIQUID_PENETRANT = "liquid_penetrant"
    EDDY_CURRENT = "eddy_current"
    ACOUSTIC_EMISSION = "acoustic_emission"
    PRESSURE_TEST = "pressure_test"
    THICKNESS_MEASUREMENT = "thickness_measurement"


class InspectionStatus(str, enum.Enum):
    """Inspection status enumeration."""
    SCHEDULED = "scheduled"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    OVERDUE = "overdue"


class FindingSeverity(str, enum.Enum):
    """Finding severity levels."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFORMATIONAL = "informational"


class InspectionResult(str, enum.Enum):
    """Overall inspection result."""
    SATISFACTORY = "satisfactory"
    ACCEPTABLE_WITH_CONDITIONS = "acceptable_with_conditions"
    REQUIRES_REPAIR = "requires_repair"
    REQUIRES_REPLACEMENT = "requires_replacement"
    UNSAFE_FOR_OPERATION = "unsafe_for_operation"


class Inspection(Base):
    """
    Inspection model for vessel inspection records.
    
    Stores inspection data, findings, and compliance
    tracking for pressure vessels and piping systems.
    """
    __tablename__ = "inspections"

    id = Column(Integer, primary_key=True, index=True)
    
    # Basic identification
    inspection_number = Column(String(100), nullable=True, unique=True, index=True)
    inspection_type = Column(Enum(InspectionType), nullable=False)
    
    # Scheduling
    scheduled_date = Column(DateTime(timezone=True), nullable=False)
    actual_start_date = Column(DateTime(timezone=True), nullable=True)
    actual_completion_date = Column(DateTime(timezone=True), nullable=True)
    
    # Inspection details
    inspection_methods = Column(JSON, nullable=False)  # List of methods used
    inspection_scope = Column(Text, nullable=True)
    inspection_procedure = Column(String(255), nullable=True)
    
    # Personnel
    inspector_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    inspection_company = Column(String(255), nullable=True)
    certification_level = Column(String(50), nullable=True)  # Level I, II, III
    
    # Conditions during inspection
    vessel_condition = Column(String(100), nullable=True)  # in_service, out_of_service, shutdown
    operating_pressure = Column(Numeric(10, 3), nullable=True)
    operating_temperature = Column(Numeric(10, 2), nullable=True)
    ambient_temperature = Column(Numeric(10, 2), nullable=True)
    weather_conditions = Column(String(100), nullable=True)
    
    # Measurements and findings
    thickness_measurements = Column(JSON, nullable=True)  # Array of measurement data
    pressure_test_results = Column(JSON, nullable=True)
    corrosion_rate_data = Column(JSON, nullable=True)
    
    # Overall assessment
    status = Column(Enum(InspectionStatus), default=InspectionStatus.SCHEDULED, nullable=False)
    overall_result = Column(Enum(InspectionResult), nullable=True)
    
    # Next inspection
    recommended_next_inspection = Column(DateTime(timezone=True), nullable=True)
    inspection_interval_months = Column(Integer, nullable=True)
    
    # Documentation
    report_path = Column(String(500), nullable=True)
    photos_path = Column(String(500), nullable=True)
    additional_documents = Column(JSON, nullable=True)
    
    # Compliance and standards
    applicable_standards = Column(JSON, nullable=True)
    compliance_status = Column(String(50), nullable=True)
    
    # Relationships
    vessel_id = Column(Integer, ForeignKey("vessels.id"), nullable=False)
    
    # Notes and comments
    inspector_notes = Column(Text, nullable=True)
    recommendations = Column(Text, nullable=True)
    
    # Audit fields
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    vessel = relationship("Vessel", back_populates="inspections")
    inspector = relationship("User", back_populates="inspections")
    findings = relationship("InspectionFinding", back_populates="inspection", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<Inspection(id={self.id}, number='{self.inspection_number}', type='{self.inspection_type}')>"

    @property
    def is_completed(self) -> bool:
        """Check if inspection is completed."""
        return self.status == InspectionStatus.COMPLETED

    @property
    def is_overdue(self) -> bool:
        """Check if inspection is overdue."""
        if self.is_completed:
            return False
        return datetime.utcnow() > self.scheduled_date

    @property
    def duration_hours(self) -> float:
        """Calculate inspection duration in hours."""
        if not self.actual_start_date or not self.actual_completion_date:
            return 0.0
        
        duration = self.actual_completion_date - self.actual_start_date
        return duration.total_seconds() / 3600

    @property
    def has_critical_findings(self) -> bool:
        """Check if inspection has critical findings."""
        if not self.findings:
            return False
        
        return any(finding.severity == FindingSeverity.CRITICAL for finding in self.findings)

    def get_minimum_thickness(self) -> float:
        """Get minimum recorded thickness."""
        if not self.thickness_measurements:
            return 0.0
        
        thicknesses = [m.get("thickness", 0) for m in self.thickness_measurements if "thickness" in m]
        return min(thicknesses) if thicknesses else 0.0

    def get_average_thickness(self) -> float:
        """Get average recorded thickness."""
        if not self.thickness_measurements:
            return 0.0
        
        thicknesses = [m.get("thickness", 0) for m in self.thickness_measurements if "thickness" in m]
        return sum(thicknesses) / len(thicknesses) if thicknesses else 0.0


class InspectionFinding(Base):
    """
    Inspection finding model for specific defects and observations.
    
    Stores individual findings from inspections including
    defects, measurements, and remedial actions.
    """
    __tablename__ = "inspection_findings"

    id = Column(Integer, primary_key=True, index=True)
    
    # Basic identification
    finding_number = Column(String(50), nullable=True)
    finding_type = Column(String(100), nullable=False)  # corrosion, crack, dent, etc.
    
    # Location and description
    location = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    
    # Severity and priority
    severity = Column(Enum(FindingSeverity), nullable=False)
    priority = Column(String(20), nullable=True)  # immediate, urgent, routine
    
    # Measurements and dimensions
    length = Column(Numeric(10, 3), nullable=True)
    width = Column(Numeric(10, 3), nullable=True)
    depth = Column(Numeric(10, 4), nullable=True)
    area = Column(Numeric(10, 3), nullable=True)
    
    # Assessment and analysis
    root_cause = Column(Text, nullable=True)
    risk_assessment = Column(Text, nullable=True)
    immediate_action_required = Column(Boolean, default=False, nullable=False)
    
    # Remedial actions
    recommended_action = Column(Text, nullable=True)
    repair_method = Column(String(255), nullable=True)
    target_completion_date = Column(DateTime(timezone=True), nullable=True)
    
    # Status tracking
    status = Column(String(50), default="open", nullable=False)  # open, in_progress, completed, closed
    resolution_date = Column(DateTime(timezone=True), nullable=True)
    resolution_description = Column(Text, nullable=True)
    
    # Documentation
    photo_references = Column(JSON, nullable=True)
    drawing_references = Column(JSON, nullable=True)
    
    # Relationships
    inspection_id = Column(Integer, ForeignKey("inspections.id"), nullable=False)
    
    # Audit fields
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    inspection = relationship("Inspection", back_populates="findings")

    def __repr__(self) -> str:
        return f"<InspectionFinding(id={self.id}, type='{self.finding_type}', severity='{self.severity}')>"

    @property
    def is_critical(self) -> bool:
        """Check if finding is critical."""
        return self.severity == FindingSeverity.CRITICAL

    @property
    def is_resolved(self) -> bool:
        """Check if finding is resolved."""
        return self.status in ["completed", "closed"]

    @property
    def is_overdue(self) -> bool:
        """Check if finding resolution is overdue."""
        if self.is_resolved or not self.target_completion_date:
            return False
        return datetime.utcnow() > self.target_completion_date
