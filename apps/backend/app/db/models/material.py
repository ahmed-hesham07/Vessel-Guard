"""
Material model for engineering material properties and specifications.

Defines material database with allowable stresses, physical properties,
and engineering data for design calculations.
"""

import enum
from typing import TYPE_CHECKING, Optional

from sqlalchemy import Boolean, Column, DateTime, Enum, Integer, String, Text, Numeric, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.base import Base


class MaterialType(str, enum.Enum):
    """Material type classification."""
    CARBON_STEEL = "carbon_steel"
    ALLOY_STEEL = "alloy_steel"
    STAINLESS_STEEL = "stainless_steel"
    ALUMINUM = "aluminum"
    COPPER_ALLOY = "copper_alloy"
    NICKEL_ALLOY = "nickel_alloy"
    TITANIUM = "titanium"
    COMPOSITE = "composite"
    PLASTIC = "plastic"
    OTHER = "other"


class MaterialStandard(str, enum.Enum):
    """Material specification standards."""
    ASME = "ASME"
    ASTM = "ASTM"
    API = "API"
    EN = "EN"
    JIS = "JIS"
    DIN = "DIN"
    BS = "BS"
    OTHER = "OTHER"


class Material(Base):
    """
    Material model for engineering material database.
    
    Stores material properties, allowable stresses, and
    specifications for design calculations.
    """
    __tablename__ = "materials"

    id = Column(Integer, primary_key=True, index=True)
    
    # Material identification
    specification = Column(String(100), nullable=False, index=True)  # e.g., "SA-516"
    grade = Column(String(50), nullable=False, index=True)  # e.g., "Grade 70"
    standard = Column(Enum(MaterialStandard), nullable=False)
    material_type = Column(Enum(MaterialType), nullable=False)
    
    # Common name and description
    common_name = Column(String(255), nullable=True)
    description = Column(Text, nullable=True)
    
    # Chemical composition (JSON for flexibility)
    chemical_composition = Column(JSON, nullable=True)  # e.g., {"C": 0.31, "Mn": 1.0, "P": 0.035}
    
    # Physical properties
    density = Column(Numeric(10, 4), nullable=True)  # lb/in³ or kg/m³
    elastic_modulus = Column(Numeric(12, 2), nullable=True)  # psi or MPa
    poisson_ratio = Column(Numeric(4, 3), nullable=True)
    coefficient_of_expansion = Column(Numeric(10, 8), nullable=True)  # in/in/°F or mm/mm/°C
    
    # Mechanical properties at room temperature
    yield_strength = Column(Numeric(10, 2), nullable=True)  # psi or MPa
    ultimate_strength = Column(Numeric(10, 2), nullable=True)  # psi or MPa
    elongation = Column(Numeric(5, 2), nullable=True)  # percentage
    hardness = Column(String(50), nullable=True)  # HB, HRC, etc.
    
    # Temperature limits
    min_design_temperature = Column(Numeric(10, 2), nullable=True)  # °F or °C
    max_design_temperature = Column(Numeric(10, 2), nullable=True)  # °F or °C
    
    # Allowable stress data (JSON for temperature-dependent values)
    allowable_stress_data = Column(JSON, nullable=True)
    # Format: {"temperatures": [70, 100, 200, 300], "stresses": [20000, 19500, 18000, 16000]}
    
    # Welding and fabrication properties
    weldability = Column(String(50), nullable=True)  # excellent, good, fair, poor
    heat_treatment_required = Column(Boolean, default=False, nullable=False)
    preheating_temperature = Column(Numeric(10, 2), nullable=True)
    interpass_temperature = Column(Numeric(10, 2), nullable=True)
    
    # Corrosion resistance
    general_corrosion_resistance = Column(String(50), nullable=True)
    pitting_resistance = Column(String(50), nullable=True)
    stress_corrosion_resistance = Column(String(50), nullable=True)
    
    # Cost and availability
    relative_cost = Column(String(20), nullable=True)  # low, medium, high
    availability = Column(String(20), nullable=True)  # readily_available, limited, special_order
    
    # Standards and certifications
    applicable_codes = Column(JSON, nullable=True)  # List of applicable design codes
    material_certifications = Column(JSON, nullable=True)  # Required certifications
    
    # Usage notes and limitations
    usage_notes = Column(Text, nullable=True)
    limitations = Column(Text, nullable=True)
    
    # Status
    is_active = Column(Boolean, default=True, nullable=False)
    is_deprecated = Column(Boolean, default=False, nullable=False)
    
    # Audit fields
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    def __repr__(self) -> str:
        return f"<Material(id={self.id}, spec='{self.specification}', grade='{self.grade}')>"

    @property
    def full_specification(self) -> str:
        """Get full material specification string."""
        return f"{self.specification} {self.grade}"

    def get_allowable_stress(self, temperature: float) -> Optional[float]:
        """
        Get allowable stress at specified temperature.
        
        Args:
            temperature: Temperature in °F or °C
            
        Returns:
            Allowable stress at given temperature, or None if not available
        """
        if not self.allowable_stress_data:
            return None
        
        temperatures = self.allowable_stress_data.get("temperatures", [])
        stresses = self.allowable_stress_data.get("stresses", [])
        
        if not temperatures or not stresses or len(temperatures) != len(stresses):
            return None
        
        # If temperature is below minimum, use minimum temperature stress
        if temperature <= temperatures[0]:
            return stresses[0]
        
        # If temperature is above maximum, use maximum temperature stress
        if temperature >= temperatures[-1]:
            return stresses[-1]
        
        # Linear interpolation for intermediate temperatures
        for i in range(len(temperatures) - 1):
            if temperatures[i] <= temperature <= temperatures[i + 1]:
                # Linear interpolation
                t1, t2 = temperatures[i], temperatures[i + 1]
                s1, s2 = stresses[i], stresses[i + 1]
                
                stress = s1 + (s2 - s1) * (temperature - t1) / (t2 - t1)
                return stress
        
        return None

    def is_suitable_for_temperature(self, temperature: float) -> bool:
        """
        Check if material is suitable for given temperature.
        
        Args:
            temperature: Operating temperature
            
        Returns:
            True if suitable, False otherwise
        """
        if self.min_design_temperature is not None and temperature < self.min_design_temperature:
            return False
        
        if self.max_design_temperature is not None and temperature > self.max_design_temperature:
            return False
        
        return True

    def is_compatible_with_code(self, design_code: str) -> bool:
        """
        Check if material is compatible with design code.
        
        Args:
            design_code: Design code (e.g., "ASME_VIII_DIV_1")
            
        Returns:
            True if compatible, False otherwise
        """
        if not self.applicable_codes:
            return False
        
        return design_code in self.applicable_codes
