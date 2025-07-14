"""
Calculation models for engineering analysis and results.

Defines calculation requests, results, and engineering analysis
data for pressure vessel and piping calculations.
"""

import enum
from datetime import datetime
from typing import TYPE_CHECKING, Dict, Any

from sqlalchemy import Boolean, Column, DateTime, Enum, ForeignKey, Integer, String, Text, Numeric, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.base import Base

if TYPE_CHECKING:
    from app.db.models.user import User
    from app.db.models.project import Project
    from app.db.models.vessel import Vessel


class CalculationType(str, enum.Enum):
    """Calculation type enumeration."""
    ASME_B31_3 = "ASME_B31_3"  # Piping stress analysis
    API_579 = "API_579"  # Fitness for service
    ASME_VIII_DIV_1 = "ASME_VIII_DIV_1"  # Pressure vessel design
    ASME_VIII_DIV_2 = "ASME_VIII_DIV_2"  # Pressure vessel alternative rules
    API_650 = "API_650"  # Storage tank design
    CUSTOM = "CUSTOM"  # Custom calculation


class CalculationStatus(str, enum.Enum):
    """Calculation status enumeration."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class ComplianceStatus(str, enum.Enum):
    """Compliance status enumeration."""
    PASS = "pass"
    FAIL = "fail"
    WARNING = "warning"
    NOT_APPLICABLE = "not_applicable"


class Calculation(Base):
    """
    Calculation model for engineering analysis requests.
    
    Stores calculation parameters, metadata, and links
    to results for engineering calculations.
    """
    __tablename__ = "calculations"

    id = Column(Integer, primary_key=True, index=True)
    
    # Basic identification
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    calculation_type = Column(Enum(CalculationType), nullable=False)
    
    # Input parameters (JSON for flexibility across calculation types)
    input_parameters = Column(JSON, nullable=False)
    
    # Calculation settings
    design_code = Column(String(50), nullable=True)
    design_standard = Column(String(50), nullable=True)
    units_system = Column(String(20), default="imperial", nullable=False)
    
    # Status and progress
    status = Column(Enum(CalculationStatus), default=CalculationStatus.PENDING, nullable=False)
    progress_percentage = Column(Integer, default=0, nullable=False)
    error_message = Column(Text, nullable=True)
    
    # Execution tracking
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    execution_time_seconds = Column(Numeric(10, 3), nullable=True)
    
    # Relationships
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    vessel_id = Column(Integer, ForeignKey("vessels.id"), nullable=True)
    calculated_by_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Audit fields
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    project = relationship("Project", back_populates="calculations")
    vessel = relationship("Vessel", back_populates="calculations")
    calculated_by = relationship("User", back_populates="calculations")
    
    # Results (one-to-one relationship)
    result = relationship("CalculationResult", back_populates="calculation", uselist=False, cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<Calculation(id={self.id}, name='{self.name}', type='{self.calculation_type}')>"

    @property
    def is_completed(self) -> bool:
        """Check if calculation is completed."""
        return self.status == CalculationStatus.COMPLETED

    @property
    def is_failed(self) -> bool:
        """Check if calculation failed."""
        return self.status == CalculationStatus.FAILED

    @property
    def has_results(self) -> bool:
        """Check if calculation has results."""
        return self.result is not None and self.is_completed

    def get_input_parameter(self, key: str, default: Any = None) -> Any:
        """Get specific input parameter value."""
        if not self.input_parameters:
            return default
        return self.input_parameters.get(key, default)

    def set_input_parameter(self, key: str, value: Any) -> None:
        """Set specific input parameter value."""
        if not self.input_parameters:
            self.input_parameters = {}
        self.input_parameters[key] = value


class CalculationResult(Base):
    """
    Calculation result model for storing engineering analysis results.
    
    Stores calculated values, compliance status, and
    engineering recommendations.
    """
    __tablename__ = "calculation_results"

    id = Column(Integer, primary_key=True, index=True)
    
    # Foreign key to calculation
    calculation_id = Column(Integer, ForeignKey("calculations.id"), nullable=False, unique=True)
    
    # Main results (JSON for flexibility)
    results = Column(JSON, nullable=False)
    
    # Compliance assessment
    compliance_status = Column(Enum(ComplianceStatus), nullable=False)
    safety_factor = Column(Numeric(10, 3), nullable=True)
    
    # Key calculated values (for easy querying)
    calculated_thickness = Column(Numeric(10, 4), nullable=True)
    allowable_pressure = Column(Numeric(10, 3), nullable=True)
    maximum_allowable_working_pressure = Column(Numeric(10, 3), nullable=True)
    stress_utilization = Column(Numeric(5, 2), nullable=True)  # Percentage
    
    # Engineering assessment
    recommendations = Column(JSON, nullable=True)  # List of recommendations
    warnings = Column(JSON, nullable=True)  # List of warnings
    critical_issues = Column(JSON, nullable=True)  # List of critical issues
    
    # Standards and references
    applicable_standards = Column(JSON, nullable=True)
    code_references = Column(JSON, nullable=True)
    
    # Detailed analysis data
    stress_analysis = Column(JSON, nullable=True)
    fatigue_analysis = Column(JSON, nullable=True)
    corrosion_analysis = Column(JSON, nullable=True)
    
    # Inspection and maintenance recommendations
    inspection_interval_years = Column(Integer, nullable=True)
    next_inspection_date = Column(DateTime(timezone=True), nullable=True)
    maintenance_recommendations = Column(JSON, nullable=True)
    
    # Quality and validation
    calculation_method = Column(String(100), nullable=True)
    validation_checks = Column(JSON, nullable=True)
    peer_reviewed = Column(Boolean, default=False, nullable=False)
    reviewed_by_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    reviewed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Report generation
    report_generated = Column(Boolean, default=False, nullable=False)
    report_path = Column(String(500), nullable=True)
    
    # Audit fields
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    calculation = relationship("Calculation", back_populates="result")
    reviewed_by = relationship("User", foreign_keys=[reviewed_by_id])

    def __repr__(self) -> str:
        return f"<CalculationResult(id={self.id}, calc_id={self.calculation_id}, status='{self.compliance_status}')>"

    @property
    def is_compliant(self) -> bool:
        """Check if result shows compliance."""
        return self.compliance_status == ComplianceStatus.PASS

    @property
    def has_warnings(self) -> bool:
        """Check if result has warnings."""
        return (self.compliance_status == ComplianceStatus.WARNING or 
                (self.warnings and len(self.warnings) > 0))

    @property
    def has_critical_issues(self) -> bool:
        """Check if result has critical issues."""
        return (self.compliance_status == ComplianceStatus.FAIL or
                (self.critical_issues and len(self.critical_issues) > 0))

    def get_result_value(self, key: str, default: Any = None) -> Any:
        """Get specific result value."""
        if not self.results:
            return default
        return self.results.get(key, default)

    def add_recommendation(self, recommendation: str, priority: str = "medium") -> None:
        """Add engineering recommendation."""
        if not self.recommendations:
            self.recommendations = []
        
        self.recommendations.append({
            "text": recommendation,
            "priority": priority,
            "timestamp": datetime.utcnow().isoformat()
        })

    def add_warning(self, warning: str, severity: str = "medium") -> None:
        """Add warning to results."""
        if not self.warnings:
            self.warnings = []
        
        self.warnings.append({
            "text": warning,
            "severity": severity,
            "timestamp": datetime.utcnow().isoformat()
        })
