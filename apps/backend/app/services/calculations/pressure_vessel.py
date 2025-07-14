"""
Engineering calculations service for pressure vessels and piping systems.

This service provides the core engineering calculations required for
pressure vessel design, analysis, and safety assessments according to
various engineering standards (ASME, API, EN, etc.).
"""

from typing import Dict, Any, Optional, List
from decimal import Decimal
import math
from enum import Enum

from sqlalchemy.orm import Session
from app.crud.calculation import calculation_crud
from app.schemas.calculation import CalculationCreate, CalculationUpdate
from app.db.models.calculation import Calculation, CalculationType
from app.db.models.material import Material
from app.db.models.vessel import Vessel


class PressureVesselStandard(str, Enum):
    """Supported pressure vessel design standards."""
    ASME_VIII_DIV1 = "ASME_VIII_DIV1"
    ASME_VIII_DIV2 = "ASME_VIII_DIV2"
    EN_13445 = "EN_13445"
    API_510 = "API_510"
    PD_5500 = "PD_5500"


class PipingStandard(str, Enum):
    """Supported piping design standards."""
    ASME_B31_1 = "ASME_B31_1"  # Power Piping
    ASME_B31_3 = "ASME_B31_3"  # Process Piping
    ASME_B31_4 = "ASME_B31_4"  # Pipeline Transportation
    ASME_B31_8 = "ASME_B31_8"  # Gas Transmission
    EN_13480 = "EN_13480"      # Metallic industrial piping


class SafetyFactor(str, Enum):
    """Safety factors for different applications."""
    NORMAL = "3.0"
    HIGH_PRESSURE = "4.0"
    CRITICAL_SERVICE = "5.0"
    TESTING = "1.5"


class CalculationService:
    """Service for performing engineering calculations."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def calculate_pressure_vessel_thickness(
        self,
        vessel_id: str,
        design_pressure: float,
        design_temperature: float,
        inner_diameter: float,
        material_id: str,
        user_id: str,
        organization_id: str,
        standard: PressureVesselStandard = PressureVesselStandard.ASME_VIII_DIV1,
        joint_efficiency: float = 1.0,
        corrosion_allowance: float = 0.0
    ) -> Dict[str, Any]:
        """
        Calculate minimum required thickness for a cylindrical pressure vessel.
        
        Args:
            vessel_id: ID of the vessel
            design_pressure: Design pressure in psi/MPa
            design_temperature: Design temperature in °F/°C
            inner_diameter: Inner diameter in inches/mm
            material_id: Material specification ID
            standard: Design standard to use
            joint_efficiency: Welding joint efficiency (0.0-1.0)
            corrosion_allowance: Corrosion allowance in inches/mm
            user_id: User performing calculation
            organization_id: Organization ID
            
        Returns:
            Dictionary containing calculation results
        """
        # Get material properties
        material = self.db.query(Material).filter(
            Material.id == material_id,
            Material.organization_id == organization_id,
            Material.is_active == True
        ).first()
        
        if not material:
            raise ValueError("Material not found or not active")
        
        # Get allowable stress for design temperature
        allowable_stress = self._get_allowable_stress(
            material, design_temperature, standard
        )
        
        # Calculate minimum thickness based on standard
        if standard == PressureVesselStandard.ASME_VIII_DIV1:
            # ASME VIII Division 1 formula: t = PR/(SE - 0.6P)
            numerator = design_pressure * inner_diameter
            denominator = 2 * allowable_stress * joint_efficiency - 1.2 * design_pressure
            
            if denominator <= 0:
                raise ValueError("Invalid parameters: stress limits exceeded")
            
            min_thickness = numerator / denominator
            
        elif standard == PressureVesselStandard.EN_13445:
            # EN 13445 formula: t = PD/(2σE - P)
            numerator = design_pressure * inner_diameter
            denominator = 2 * allowable_stress * joint_efficiency - design_pressure
            
            if denominator <= 0:
                raise ValueError("Invalid parameters: stress limits exceeded")
            
            min_thickness = numerator / denominator
            
        else:
            raise NotImplementedError(f"Standard {standard} not implemented")
        
        # Add corrosion allowance
        required_thickness = min_thickness + corrosion_allowance
        
        # Safety check
        if required_thickness > inner_diameter * 0.5:
            raise ValueError("Required thickness exceeds practical limits")
        
        # Prepare calculation results
        results = {
            "minimum_thickness": round(min_thickness, 4),
            "required_thickness": round(required_thickness, 4),
            "design_pressure": design_pressure,
            "design_temperature": design_temperature,
            "allowable_stress": allowable_stress,
            "joint_efficiency": joint_efficiency,
            "corrosion_allowance": corrosion_allowance,
            "standard": standard,
            "material": {
                "name": material.name,
                "specification": material.specification,
                "grade": material.grade
            },
            "safety_margin": round(
                ((allowable_stress * joint_efficiency) / design_pressure - 1) * 100, 2
            )
        }
        
        # Save calculation to database
        calc_data = CalculationCreate(
            vessel_id=vessel_id,
            calculation_type=CalculationType.PRESSURE_VESSEL_THICKNESS,
            parameters={
                "design_pressure": design_pressure,
                "design_temperature": design_temperature,
                "inner_diameter": inner_diameter,
                "material_id": material_id,
                "standard": standard,
                "joint_efficiency": joint_efficiency,
                "corrosion_allowance": corrosion_allowance
            },
            results=results,
            status="completed",
            notes=f"Thickness calculation per {standard}"
        )
        
        calculation = calculation_crud.create_with_user(
            db=self.db,
            obj_in=calc_data,
            user_id=user_id,
            organization_id=organization_id
        )
        
        results["calculation_id"] = calculation.id
        return results
    
    def calculate_piping_thickness(
        self,
        design_pressure: float,
        outer_diameter: float,
        material_id: str,
        user_id: str,
        organization_id: str,
        standard: PipingStandard = PipingStandard.ASME_B31_3,
        design_temperature: float = 70.0,
        corrosion_allowance: float = 0.0
    ) -> Dict[str, Any]:
        """
        Calculate minimum wall thickness for piping per ASME B31.3 or similar.
        
        Args:
            design_pressure: Internal design pressure
            outer_diameter: Outside diameter of pipe
            material_id: Material specification ID
            standard: Piping design standard
            design_temperature: Design temperature
            corrosion_allowance: Corrosion allowance
            user_id: User performing calculation
            organization_id: Organization ID
            
        Returns:
            Dictionary containing calculation results
        """
        # Get material properties
        material = self.db.query(Material).filter(
            Material.id == material_id,
            Material.organization_id == organization_id,
            Material.is_active == True
        ).first()
        
        if not material:
            raise ValueError("Material not found or not active")
        
        # Get allowable stress
        allowable_stress = self._get_allowable_stress(
            material, design_temperature, standard
        )
        
        # Calculate minimum thickness
        if standard in [PipingStandard.ASME_B31_1, PipingStandard.ASME_B31_3]:
            # ASME B31.3 formula: t = PD/(2SE + P)
            numerator = design_pressure * outer_diameter
            denominator = 2 * allowable_stress + design_pressure
            min_thickness = numerator / denominator
            
        else:
            raise NotImplementedError(f"Standard {standard} not implemented")
        
        # Add corrosion allowance
        required_thickness = min_thickness + corrosion_allowance
        
        results = {
            "minimum_thickness": round(min_thickness, 4),
            "required_thickness": round(required_thickness, 4),
            "design_pressure": design_pressure,
            "outer_diameter": outer_diameter,
            "allowable_stress": allowable_stress,
            "standard": standard,
            "material": {
                "name": material.name,
                "specification": material.specification
            }
        }
        
        return results
    
    def calculate_hydrostatic_test_pressure(
        self,
        design_pressure: float,
        design_temperature: float,
        test_temperature: float,
        standard: PressureVesselStandard = PressureVesselStandard.ASME_VIII_DIV1
    ) -> Dict[str, Any]:
        """
        Calculate hydrostatic test pressure for pressure vessels.
        
        Args:
            design_pressure: Design pressure
            design_temperature: Design temperature
            test_temperature: Test temperature
            standard: Design standard
            
        Returns:
            Dictionary containing test pressure calculation
        """
        if standard == PressureVesselStandard.ASME_VIII_DIV1:
            # ASME VIII Div 1: Test pressure = 1.3 * Design Pressure
            test_pressure = 1.3 * design_pressure
            
        elif standard == PressureVesselStandard.EN_13445:
            # EN 13445: Test pressure = 1.25 * Design Pressure
            test_pressure = 1.25 * design_pressure
            
        else:
            # Default safety factor
            test_pressure = 1.3 * design_pressure
        
        return {
            "test_pressure": round(test_pressure, 2),
            "design_pressure": design_pressure,
            "test_factor": round(test_pressure / design_pressure, 2),
            "standard": standard,
            "test_temperature": test_temperature,
            "design_temperature": design_temperature
        }
    
    def calculate_vessel_volume(
        self,
        length: float,
        diameter: float,
        head_type: str = "ellipsoidal",
        head_height: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Calculate vessel internal volume.
        
        Args:
            length: Cylindrical length
            diameter: Internal diameter
            head_type: Type of heads (ellipsoidal, torispherical, flat, hemispherical)
            head_height: Height of heads if not standard
            
        Returns:
            Dictionary containing volume calculations
        """
        radius = diameter / 2
        
        # Cylindrical volume
        cylindrical_volume = math.pi * radius ** 2 * length
        
        # Head volume calculation
        if head_type == "ellipsoidal":
            # Standard 2:1 ellipsoidal head
            head_volume = (math.pi * diameter ** 3) / 12
        elif head_type == "hemispherical":
            head_volume = (2 * math.pi * radius ** 3) / 3
        elif head_type == "torispherical":
            # Approximate for standard torispherical head
            head_volume = (math.pi * diameter ** 3) / 24
        elif head_type == "flat":
            head_volume = 0
        else:
            head_volume = 0
        
        # Total volume (2 heads)
        total_volume = cylindrical_volume + (2 * head_volume)
        
        return {
            "total_volume": round(total_volume, 2),
            "cylindrical_volume": round(cylindrical_volume, 2),
            "head_volume": round(head_volume, 2),
            "head_type": head_type,
            "length": length,
            "diameter": diameter
        }
    
    def _get_allowable_stress(
        self,
        material: Material,
        temperature: float,
        standard: str
    ) -> float:
        """
        Get allowable stress for material at given temperature.
        
        This is a simplified implementation. In practice, this would
        reference detailed stress tables from the applicable standards.
        """
        # Default allowable stress calculation
        # This should be replaced with actual stress tables
        base_stress = material.yield_strength * 0.67  # Basic allowable stress
        
        # Temperature adjustment (simplified)
        if temperature > 100:  # Above 100°F/°C
            temp_factor = 1.0 - (temperature - 100) * 0.001
            base_stress *= max(temp_factor, 0.5)  # Minimum 50% of base
        
        return base_stress
    
    def validate_calculation_parameters(
        self,
        calculation_type: CalculationType,
        parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Validate calculation parameters before performing calculations.
        
        Args:
            calculation_type: Type of calculation
            parameters: Calculation parameters
            
        Returns:
            Dictionary with validation results
        """
        errors = []
        warnings = []
        
        if calculation_type == CalculationType.PRESSURE_VESSEL_THICKNESS:
            # Check required parameters
            required = ["design_pressure", "inner_diameter", "material_id"]
            for param in required:
                if param not in parameters or parameters[param] is None:
                    errors.append(f"Required parameter '{param}' is missing")
            
            # Validate ranges
            if "design_pressure" in parameters:
                pressure = parameters["design_pressure"]
                if pressure <= 0:
                    errors.append("Design pressure must be positive")
                elif pressure > 10000:  # Example limit
                    warnings.append("Design pressure is very high")
            
            if "inner_diameter" in parameters:
                diameter = parameters["inner_diameter"]
                if diameter <= 0:
                    errors.append("Diameter must be positive")
        
        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings
        }


def get_calculation_service(db: Session) -> CalculationService:
    """Factory function to get calculation service instance."""
    return CalculationService(db)
