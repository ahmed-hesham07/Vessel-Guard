"""
Validation service for engineering parameters and business rules.

Provides comprehensive validation for calculation parameters,
vessel specifications, and compliance requirements.
"""

from typing import Dict, Any, List, Optional, Tuple
from decimal import Decimal
import re

from app.utils.engineering import EngineeringUtils
from app.core.logging_config import get_logger

logger = get_logger(__name__)


class ValidationService:
    """Service for validating engineering parameters and business rules."""
    
    def __init__(self):
        self.engineering_utils = EngineeringUtils()
        
        # Define validation rules for different calculation types
        self.calculation_rules = {
            "ASME_VIII_DIV_1": {
                "required_fields": [
                    "design_pressure", "design_temperature", "inside_diameter", 
                    "wall_thickness", "material_specification", "joint_efficiency"
                ],
                "field_rules": {
                    "design_pressure": {
                        "type": float,
                        "min_value": 0.1,
                        "max_value": 10000.0,
                        "unit": "psi"
                    },
                    "design_temperature": {
                        "type": float,
                        "min_value": -50.0,
                        "max_value": 1000.0,
                        "unit": "°F"
                    },
                    "inside_diameter": {
                        "type": float,
                        "min_value": 0.1,
                        "max_value": 1000.0,
                        "unit": "inches"
                    },
                    "wall_thickness": {
                        "type": float,
                        "min_value": 0.01,
                        "max_value": 10.0,
                        "unit": "inches"
                    },
                    "joint_efficiency": {
                        "type": float,
                        "min_value": 0.0,
                        "max_value": 1.0,
                        "unit": "dimensionless"
                    },
                    "corrosion_allowance": {
                        "type": float,
                        "min_value": 0.0,
                        "max_value": 1.0,
                        "unit": "inches"
                    }
                }
            },
            "ASME_B31_3": {
                "required_fields": [
                    "design_pressure", "design_temperature", "nominal_diameter",
                    "schedule", "material_specification"
                ],
                "field_rules": {
                    "design_pressure": {
                        "type": float,
                        "min_value": 0.1,
                        "max_value": 5000.0,
                        "unit": "psi"
                    },
                    "design_temperature": {
                        "type": float,
                        "min_value": -50.0,
                        "max_value": 1000.0,
                        "unit": "°F"
                    },
                    "nominal_diameter": {
                        "type": float,
                        "min_value": 0.125,
                        "max_value": 48.0,
                        "unit": "inches"
                    },
                    "schedule": {
                        "type": str,
                        "allowed_values": ["5S", "10S", "40S", "80S", "160S", "XXS"]
                    }
                }
            },
            "API_579": {
                "required_fields": [
                    "current_thickness", "original_thickness", "design_pressure",
                    "design_temperature", "material_specification"
                ],
                "field_rules": {
                    "current_thickness": {
                        "type": float,
                        "min_value": 0.01,
                        "max_value": 10.0,
                        "unit": "inches"
                    },
                    "original_thickness": {
                        "type": float,
                        "min_value": 0.01,
                        "max_value": 10.0,
                        "unit": "inches"
                    },
                    "design_pressure": {
                        "type": float,
                        "min_value": 0.1,
                        "max_value": 10000.0,
                        "unit": "psi"
                    },
                    "design_temperature": {
                        "type": float,
                        "min_value": -50.0,
                        "max_value": 1000.0,
                        "unit": "°F"
                    }
                }
            }
        }
        
        # Material validation rules
        self.material_rules = {
            "SA-516 Grade 70": {
                "max_temperature": 650,
                "min_temperature": -20,
                "yield_strength": 38000,
                "tensile_strength": 70000
            },
            "SA-106 Grade B": {
                "max_temperature": 800,
                "min_temperature": -20,
                "yield_strength": 35000,
                "tensile_strength": 60000
            },
            "SA-335 P11": {
                "max_temperature": 1000,
                "min_temperature": -20,
                "yield_strength": 45000,
                "tensile_strength": 85000
            }
        }

    def validate_calculation_parameters(
        self, 
        parameters: Dict[str, Any], 
        calculation_type: str
    ) -> Dict[str, Any]:
        """
        Validate calculation parameters against engineering rules.
        
        Args:
            parameters: Dictionary of input parameters
            calculation_type: Type of calculation being performed
            
        Returns:
            Dictionary with validation results
        """
        errors = []
        warnings = []
        
        # Get validation rules for calculation type
        rules = self.calculation_rules.get(calculation_type)
        if not rules:
            errors.append(f"Unknown calculation type: {calculation_type}")
            return {"valid": False, "errors": errors, "warnings": warnings}
        
        # Check required fields
        for field in rules["required_fields"]:
            if field not in parameters or parameters[field] is None:
                errors.append(f"Required field '{field}' is missing")
        
        # Validate field values
        field_rules = rules.get("field_rules", {})
        for field, value in parameters.items():
            if field not in field_rules:
                continue
                
            field_rule = field_rules[field]
            
            # Type validation
            if "type" in field_rule:
                if not isinstance(value, field_rule["type"]):
                    errors.append(f"Field '{field}' must be of type {field_rule['type'].__name__}")
                    continue
            
            # Range validation
            if isinstance(value, (int, float, Decimal)):
                if "min_value" in field_rule and value < field_rule["min_value"]:
                    errors.append(
                        f"Field '{field}' must be >= {field_rule['min_value']} {field_rule.get('unit', '')}"
                    )
                
                if "max_value" in field_rule and value > field_rule["max_value"]:
                    errors.append(
                        f"Field '{field}' must be <= {field_rule['max_value']} {field_rule.get('unit', '')}"
                    )
            
            # Allowed values validation
            if "allowed_values" in field_rule:
                if value not in field_rule["allowed_values"]:
                    errors.append(
                        f"Field '{field}' must be one of: {', '.join(field_rule['allowed_values'])}"
                    )
        
        # Cross-field validation
        cross_validation_result = self._validate_cross_field_rules(parameters, calculation_type)
        errors.extend(cross_validation_result["errors"])
        warnings.extend(cross_validation_result["warnings"])
        
        # Material-specific validation
        if "material_specification" in parameters:
            material_validation = self._validate_material_compatibility(
                parameters["material_specification"],
                parameters.get("design_temperature"),
                calculation_type
            )
            errors.extend(material_validation["errors"])
            warnings.extend(material_validation["warnings"])
        
        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings
        }

    def _validate_cross_field_rules(
        self, 
        parameters: Dict[str, Any], 
        calculation_type: str
    ) -> Dict[str, List[str]]:
        """Validate relationships between different fields."""
        errors = []
        warnings = []
        
        if calculation_type == "ASME_VIII_DIV_1":
            # Check thickness to diameter ratio
            if "wall_thickness" in parameters and "inside_diameter" in parameters:
                thickness = parameters["wall_thickness"]
                diameter = parameters["inside_diameter"]
                
                if diameter > 0:
                    ratio = thickness / diameter
                    if ratio > 0.1:
                        warnings.append(
                            f"Thickness to diameter ratio ({ratio:.3f}) is high. "
                            "Consider using ASME VIII Div 2 for thick-walled vessels."
                        )
                    elif ratio < 0.001:
                        warnings.append(
                            f"Thickness to diameter ratio ({ratio:.3f}) is very low. "
                            "Verify minimum thickness requirements."
                        )
            
            # Check pressure and temperature relationship
            if "design_pressure" in parameters and "design_temperature" in parameters:
                pressure = parameters["design_pressure"]
                temperature = parameters["design_temperature"]
                
                if temperature > 750 and pressure > 1000:
                    warnings.append(
                        "High pressure and temperature combination detected. "
                        "Consider material selection and design code requirements."
                    )
        
        elif calculation_type == "API_579":
            # Check thickness loss
            if "current_thickness" in parameters and "original_thickness" in parameters:
                current = parameters["current_thickness"]
                original = parameters["original_thickness"]
                
                if original > 0:
                    loss_ratio = (original - current) / original
                    if loss_ratio > 0.5:
                        errors.append(
                            f"Thickness loss ratio ({loss_ratio:.1%}) exceeds 50%. "
                            "Component may require replacement."
                        )
                    elif loss_ratio > 0.2:
                        warnings.append(
                            f"Significant thickness loss detected ({loss_ratio:.1%}). "
                            "Consider detailed fitness-for-service assessment."
                        )
        
        return {"errors": errors, "warnings": warnings}

    def _validate_material_compatibility(
        self, 
        material: str, 
        temperature: Optional[float], 
        calculation_type: str
    ) -> Dict[str, List[str]]:
        """Validate material compatibility with operating conditions."""
        errors = []
        warnings = []
        
        if material not in self.material_rules:
            warnings.append(f"Material '{material}' not in validation database")
            return {"errors": errors, "warnings": warnings}
        
        material_rule = self.material_rules[material]
        
        if temperature is not None:
            if temperature > material_rule["max_temperature"]:
                errors.append(
                    f"Design temperature ({temperature}°F) exceeds maximum "
                    f"for {material} ({material_rule['max_temperature']}°F)"
                )
            elif temperature < material_rule["min_temperature"]:
                errors.append(
                    f"Design temperature ({temperature}°F) below minimum "
                    f"for {material} ({material_rule['min_temperature']}°F)"
                )
        
        return {"errors": errors, "warnings": warnings}

    def validate_vessel_data(self, vessel_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate vessel design data.
        
        Args:
            vessel_data: Dictionary containing vessel specifications
            
        Returns:
            Dictionary with validation results
        """
        errors = []
        warnings = []
        
        # Required fields
        required_fields = [
            "tag_number", "name", "vessel_type", "design_pressure",
            "design_temperature", "material_specification"
        ]
        
        for field in required_fields:
            if field not in vessel_data or not vessel_data[field]:
                errors.append(f"Required field '{field}' is missing")
        
        # Tag number format validation
        if "tag_number" in vessel_data:
            tag = vessel_data["tag_number"]
            if not re.match(r"^[A-Z0-9\-_]{1,20}$", tag):
                errors.append(
                    "Tag number must contain only letters, numbers, hyphens, and underscores "
                    "(1-20 characters)"
                )
        
        # Pressure and temperature validation
        if "design_pressure" in vessel_data:
            pressure = vessel_data["design_pressure"]
            if not isinstance(pressure, (int, float, Decimal)) or pressure <= 0:
                errors.append("Design pressure must be a positive number")
            elif pressure > 10000:
                warnings.append("Design pressure is very high. Verify design requirements.")
        
        if "design_temperature" in vessel_data:
            temperature = vessel_data["design_temperature"]
            if not isinstance(temperature, (int, float, Decimal)):
                errors.append("Design temperature must be a number")
            elif temperature < -50 or temperature > 1000:
                warnings.append("Design temperature is outside typical range")
        
        # Material validation
        if "material_specification" in vessel_data:
            material = vessel_data["material_specification"]
            if material not in self.material_rules:
                warnings.append(f"Material '{material}' not in validation database")
        
        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings
        }

    def validate_project_data(self, project_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate project information.
        
        Args:
            project_data: Dictionary containing project specifications
            
        Returns:
            Dictionary with validation results
        """
        errors = []
        warnings = []
        
        # Required fields
        required_fields = ["name", "description", "start_date"]
        
        for field in required_fields:
            if field not in project_data or not project_data[field]:
                errors.append(f"Required field '{field}' is missing")
        
        # Date validation
        if "start_date" in project_data and "end_date" in project_data:
            try:
                from datetime import datetime
                start_date = datetime.fromisoformat(project_data["start_date"].replace('Z', '+00:00'))
                end_date = datetime.fromisoformat(project_data["end_date"].replace('Z', '+00:00'))
                
                if end_date <= start_date:
                    errors.append("End date must be after start date")
                    
            except (ValueError, TypeError):
                errors.append("Invalid date format")
        
        # Name validation
        if "name" in project_data:
            name = project_data["name"]
            if len(name) < 3:
                errors.append("Project name must be at least 3 characters long")
            elif len(name) > 255:
                errors.append("Project name must be 255 characters or less")
        
        # Priority validation
        if "priority" in project_data:
            priority = project_data["priority"]
            allowed_priorities = ["low", "medium", "high", "critical"]
            if priority not in allowed_priorities:
                errors.append(f"Priority must be one of: {', '.join(allowed_priorities)}")
        
        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings
        }

    def validate_user_permissions(
        self, 
        user_permissions: Dict[str, Any], 
        required_permissions: List[str]
    ) -> Dict[str, Any]:
        """
        Validate user permissions for specific operations.
        
        Args:
            user_permissions: Dictionary of user permissions
            required_permissions: List of required permissions
            
        Returns:
            Dictionary with validation results
        """
        errors = []
        warnings = []
        
        for permission in required_permissions:
            if permission not in user_permissions or not user_permissions[permission]:
                errors.append(f"Required permission '{permission}' is missing")
        
        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings
        } 