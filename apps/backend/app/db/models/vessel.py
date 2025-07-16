"""
Vessel model for pressure vessel and piping system definitions.

Defines pressure vessels, tanks, and piping components
with their design specifications and properties.
"""

import enum
from datetime import datetime
from typing import TYPE_CHECKING, List

from sqlalchemy import Boolean, Column, DateTime, Enum, ForeignKey, Integer, String, Text, Numeric, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.base import Base

if TYPE_CHECKING:
    from app.db.models.project import Project
    from app.db.models.material import Material
    from app.db.models.calculation import Calculation
    from app.db.models.inspection import Inspection


class VesselType(str, enum.Enum):
    """Vessel type enumeration."""
    PRESSURE_VESSEL = "pressure_vessel"
    STORAGE_TANK = "storage_tank"
    HEAT_EXCHANGER = "heat_exchanger"
    REACTOR = "reactor"
    SEPARATOR = "separator"
    PIPING = "piping"
    AIR_COOLING = "air_cooling"
    FITTING = "fitting"
    VALVE = "valve"


class VesselGeometry(str, enum.Enum):
    """Vessel geometry types."""
    CYLINDRICAL = "cylindrical"
    SPHERICAL = "spherical"
    CONICAL = "conical"
    RECTANGULAR = "rectangular"
    CUSTOM = "custom"


class DesignCode(str, enum.Enum):
    """Design codes and standards."""
    ASME_VIII_DIV_1 = "ASME_VIII_DIV_1"
    ASME_VIII_DIV_2 = "ASME_VIII_DIV_2"
    ASME_B31_3 = "ASME_B31_3"
    ASME_B31_1 = "ASME_B31_1"
    API_650 = "API_650"
    API_653 = "API_653"
    EN_13445 = "EN_13445"
    PD_5500 = "PD_5500"


class Vessel(Base):
    """
    Vessel model for pressure vessels and piping components.
    
    Stores design specifications, operating conditions,
    and material properties for engineering analysis.
    """
    __tablename__ = "vessels"

    id = Column(Integer, primary_key=True, index=True)
    
    # Basic identification
    tag_number = Column(String(100), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    
    # Vessel classification
    vessel_type = Column(Enum(VesselType), nullable=False)
    geometry = Column(Enum(VesselGeometry), nullable=False)
    
    # Design conditions
    design_pressure = Column(Numeric(10, 3), nullable=False)  # Design pressure
    design_temperature = Column(Numeric(10, 2), nullable=False)  # Design temperature
    operating_pressure = Column(Numeric(10, 3), nullable=True)  # Normal operating pressure
    operating_temperature = Column(Numeric(10, 2), nullable=True)  # Normal operating temperature
    
    # Physical dimensions
    diameter = Column(Numeric(10, 3), nullable=True)  # Outside diameter
    length = Column(Numeric(10, 3), nullable=True)  # Length or height
    wall_thickness = Column(Numeric(10, 4), nullable=False)  # Wall thickness
    
    # Additional dimensions for complex geometries
    inner_diameter = Column(Numeric(10, 3), nullable=True)
    head_thickness = Column(Numeric(10, 4), nullable=True)
    head_type = Column(String(50), nullable=True)  # elliptical, hemispherical, flat, etc.
    
    # Material properties
    material_specification = Column(String(100), nullable=False)
    material_grade = Column(String(50), nullable=True)
    
    # Design parameters
    design_code = Column(Enum(DesignCode), nullable=False)
    joint_efficiency = Column(Numeric(4, 3), default=1.0, nullable=False)
    corrosion_allowance = Column(Numeric(10, 4), default=0.0, nullable=False)
    
    # Fabrication and testing
    fabrication_year = Column(Integer, nullable=True)
    manufacturer = Column(String(255), nullable=True)
    heat_treatment = Column(String(100), nullable=True)
    welding_procedure = Column(String(100), nullable=True)
    
    # Testing and inspection
    hydrostatic_test_pressure = Column(Numeric(10, 3), nullable=True)
    pneumatic_test_pressure = Column(Numeric(10, 3), nullable=True)
    radiographic_examination = Column(String(50), nullable=True)  # full, spot, none
    
    # Service conditions
    service_fluid = Column(String(255), nullable=True)
    fluid_density = Column(Numeric(10, 3), nullable=True)
    fluid_viscosity = Column(Numeric(10, 6), nullable=True)
    corrosion_rate = Column(Numeric(10, 4), nullable=True)  # mils per year or mm per year
    
    # Location and environment
    location = Column(String(255), nullable=True)
    environment = Column(String(100), nullable=True)  # indoor, outdoor, marine, etc.
    insulation_type = Column(String(100), nullable=True)
    
    # Safety factors and margins
    safety_factor = Column(Numeric(4, 2), nullable=True)
    design_margin = Column(Numeric(4, 2), nullable=True)
    
    # Inspection and maintenance
    inspection_interval_years = Column(Integer, nullable=True)
    next_inspection_date = Column(DateTime(timezone=True), nullable=True)
    last_inspection_date = Column(DateTime(timezone=True), nullable=True)
    
    # Status and lifecycle
    is_active = Column(Boolean, default=True, nullable=False)
    commissioning_date = Column(DateTime(timezone=True), nullable=True)
    decommissioning_date = Column(DateTime(timezone=True), nullable=True)
    
    # Project relationship
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    
    # Custom properties (JSON for flexibility)
    custom_properties = Column(JSON, nullable=True)
    
    # Notes and comments
    notes = Column(Text, nullable=True)
    
    # Audit fields
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    project = relationship("Project", back_populates="vessels")
    calculations = relationship("Calculation", back_populates="vessel", cascade="all, delete-orphan")
    inspections = relationship("Inspection", back_populates="vessel", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<Vessel(id={self.id}, tag='{self.tag_number}', type='{self.vessel_type}')>"

    @property
    def pressure_ratio(self) -> float:
        """Calculate operating to design pressure ratio."""
        if not self.operating_pressure or self.design_pressure <= 0:
            return 0.0
        return float(self.operating_pressure / self.design_pressure)

    @property
    def requires_inspection(self) -> bool:
        """Check if vessel requires inspection."""
        if not self.next_inspection_date:
            return True
        return datetime.utcnow() >= self.next_inspection_date

    @property
    def is_in_service(self) -> bool:
        """Check if vessel is currently in service."""
        now = datetime.utcnow()
        
        if not self.is_active:
            return False
        
        if self.commissioning_date and now < self.commissioning_date:
            return False
        
        if self.decommissioning_date and now >= self.decommissioning_date:
            return False
        
        return True

    def calculate_minimum_thickness(self) -> float:
        """Calculate minimum required thickness (basic calculation)."""
        # This is a simplified calculation - real implementation would use
        # specific design code formulas
        if self.design_pressure <= 0:
            return 0.0
        
        # Basic thin-wall pressure vessel formula: t = PR/(SE - 0.6P)
        # Where: P = pressure, R = radius, S = allowable stress, E = efficiency
        
        radius = float(self.diameter) / 2 if self.diameter else 0
        
        # Assuming typical allowable stress of 20,000 psi for carbon steel
        allowable_stress = 20000
        efficiency = float(self.joint_efficiency)
        pressure = float(self.design_pressure)
        
        if allowable_stress * efficiency <= 0.6 * pressure:
            return float('inf')  # Invalid condition
        
        thickness = (pressure * radius) / (allowable_stress * efficiency - 0.6 * pressure)
        
        # Add corrosion allowance
        return thickness + float(self.corrosion_allowance)
