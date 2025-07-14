"""
Engineering utilities and helper functions for Vessel Guard.

This module provides common engineering calculations, unit conversions,
and utility functions used throughout the application.
"""

import math
from typing import Dict, Any, Union, Optional
from decimal import Decimal, ROUND_HALF_UP
from enum import Enum
import numpy as np


class UnitSystem(str, Enum):
    """Unit system enumeration."""
    US_CUSTOMARY = "US_CUSTOMARY"  # psi, inches, °F, etc.
    METRIC = "METRIC"              # MPa, mm, °C, etc.
    SI = "SI"                      # Pa, m, K, etc.


class PressureUnit(str, Enum):
    """Pressure unit enumeration."""
    PSI = "psi"
    PSIG = "psig"
    PSIA = "psia"
    KPA = "kPa"
    MPA = "MPa"
    BAR = "bar"
    MBAR = "mbar"
    PA = "Pa"
    ATM = "atm"
    TORR = "torr"


class LengthUnit(str, Enum):
    """Length unit enumeration."""
    INCH = "in"
    FOOT = "ft"
    MM = "mm"
    CM = "cm"
    M = "m"
    MIL = "mil"  # thousandths of an inch


class TemperatureUnit(str, Enum):
    """Temperature unit enumeration."""
    FAHRENHEIT = "°F"
    CELSIUS = "°C"
    KELVIN = "K"
    RANKINE = "°R"


class EngineeringUtils:
    """Utility class for engineering calculations and conversions."""
    
    # Conversion factors to base units
    PRESSURE_TO_PA = {
        "psi": 6894.757,
        "psig": 6894.757,
        "psia": 6894.757,
        "kpa": 1000,
        "mpa": 1000000,
        "bar": 100000,
        "mbar": 100,
        "pa": 1,
        "atm": 101325,
        "torr": 133.322
    }
    
    LENGTH_TO_M = {
        "in": 0.0254,
        "ft": 0.3048,
        "mm": 0.001,
        "cm": 0.01,
        "m": 1,
        "mil": 0.0000254
    }
    
    @staticmethod
    def convert_pressure(
        value: float,
        from_unit: str,
        to_unit: str
    ) -> float:
        """
        Convert pressure between different units.
        
        Args:
            value: Pressure value to convert
            from_unit: Source unit
            to_unit: Target unit
            
        Returns:
            Converted pressure value
        """
        if from_unit == to_unit:
            return value
        
        # Convert to Pa first, then to target unit
        pa_value = value * EngineeringUtils.PRESSURE_TO_PA[from_unit.lower()]
        return pa_value / EngineeringUtils.PRESSURE_TO_PA[to_unit.lower()]
    
    @staticmethod
    def convert_length(
        value: float,
        from_unit: str,
        to_unit: str
    ) -> float:
        """
        Convert length between different units.
        
        Args:
            value: Length value to convert
            from_unit: Source unit
            to_unit: Target unit
            
        Returns:
            Converted length value
        """
        if from_unit == to_unit:
            return value
        
        # Convert to meters first, then to target unit
        m_value = value * EngineeringUtils.LENGTH_TO_M[from_unit.lower()]
        return m_value / EngineeringUtils.LENGTH_TO_M[to_unit.lower()]
    
    @staticmethod
    def convert_temperature(
        value: float,
        from_unit: str,
        to_unit: str
    ) -> float:
        """
        Convert temperature between different units.
        
        Args:
            value: Temperature value to convert
            from_unit: Source unit (°F, °C, K, °R)
            to_unit: Target unit
            
        Returns:
            Converted temperature value
        """
        if from_unit == to_unit:
            return value
        
        # Convert to Celsius first
        if from_unit == "°F":
            celsius = (value - 32) * 5/9
        elif from_unit == "K":
            celsius = value - 273.15
        elif from_unit == "°R":
            celsius = (value - 491.67) * 5/9
        else:  # °C
            celsius = value
        
        # Convert from Celsius to target
        if to_unit == "°F":
            return celsius * 9/5 + 32
        elif to_unit == "K":
            return celsius + 273.15
        elif to_unit == "°R":
            return celsius * 9/5 + 491.67
        else:  # °C
            return celsius
    
    @staticmethod
    def round_engineering(
        value: float,
        significant_figures: int = 4
    ) -> float:
        """
        Round a value to specified significant figures for engineering use.
        
        Args:
            value: Value to round
            significant_figures: Number of significant figures
            
        Returns:
            Rounded value
        """
        if value == 0:
            return 0
        
        # Calculate the order of magnitude
        magnitude = math.floor(math.log10(abs(value)))
        
        # Calculate the factor to shift decimal places
        factor = 10 ** (significant_figures - 1 - magnitude)
        
        # Round and shift back
        return round(value * factor) / factor
    
    @staticmethod
    def calculate_stress(
        force: float,
        area: float,
        force_unit: str = "lbf",
        area_unit: str = "in²"
    ) -> Dict[str, float]:
        """
        Calculate stress from force and area.
        
        Args:
            force: Applied force
            area: Cross-sectional area
            force_unit: Unit of force
            area_unit: Unit of area
            
        Returns:
            Dictionary with stress in various units
        """
        # Convert to base units (N and m²)
        force_conversion = {
            "lbf": 4.448222,
            "N": 1,
            "kN": 1000,
            "kgf": 9.80665
        }
        
        area_conversion = {
            "in²": 0.00064516,  # to m²
            "ft²": 0.092903,
            "mm²": 0.000001,
            "cm²": 0.0001,
            "m²": 1
        }
        
        force_n = force * force_conversion.get(force_unit, 1)
        area_m2 = area * area_conversion.get(area_unit, 1)
        
        if area_m2 == 0:
            raise ValueError("Area cannot be zero")
        
        stress_pa = force_n / area_m2
        
        return {
            "Pa": stress_pa,
            "kPa": stress_pa / 1000,
            "MPa": stress_pa / 1000000,
            "psi": stress_pa / 6894.757,
            "ksi": stress_pa / 6894757
        }
    
    @staticmethod
    def calculate_strain(
        original_length: float,
        final_length: float
    ) -> float:
        """
        Calculate engineering strain.
        
        Args:
            original_length: Original length
            final_length: Final length after deformation
            
        Returns:
            Engineering strain (dimensionless)
        """
        if original_length == 0:
            raise ValueError("Original length cannot be zero")
        
        return (final_length - original_length) / original_length
    
    @staticmethod
    def calculate_elastic_modulus(
        stress: float,
        strain: float
    ) -> float:
        """
        Calculate elastic modulus (Young's modulus).
        
        Args:
            stress: Applied stress
            strain: Resulting strain
            
        Returns:
            Elastic modulus in same units as stress
        """
        if strain == 0:
            raise ValueError("Strain cannot be zero")
        
        return stress / strain
    
    @staticmethod
    def calculate_safety_factor(
        ultimate_strength: float,
        working_stress: float
    ) -> float:
        """
        Calculate safety factor.
        
        Args:
            ultimate_strength: Ultimate strength of material
            working_stress: Applied working stress
            
        Returns:
            Safety factor
        """
        if working_stress == 0:
            raise ValueError("Working stress cannot be zero")
        
        return ultimate_strength / working_stress
    
    @staticmethod
    def calculate_hoop_stress(
        internal_pressure: float,
        inner_diameter: float,
        wall_thickness: float
    ) -> float:
        """
        Calculate hoop stress in a cylindrical pressure vessel.
        
        Args:
            internal_pressure: Internal pressure
            inner_diameter: Inner diameter
            wall_thickness: Wall thickness
            
        Returns:
            Hoop stress
        """
        if wall_thickness == 0:
            raise ValueError("Wall thickness cannot be zero")
        
        return (internal_pressure * inner_diameter) / (2 * wall_thickness)
    
    @staticmethod
    def calculate_longitudinal_stress(
        internal_pressure: float,
        inner_diameter: float,
        wall_thickness: float
    ) -> float:
        """
        Calculate longitudinal stress in a cylindrical pressure vessel.
        
        Args:
            internal_pressure: Internal pressure
            inner_diameter: Inner diameter
            wall_thickness: Wall thickness
            
        Returns:
            Longitudinal stress
        """
        if wall_thickness == 0:
            raise ValueError("Wall thickness cannot be zero")
        
        return (internal_pressure * inner_diameter) / (4 * wall_thickness)
    
    @staticmethod
    def calculate_von_mises_stress(
        sigma_1: float,
        sigma_2: float,
        sigma_3: float = 0
    ) -> float:
        """
        Calculate von Mises equivalent stress.
        
        Args:
            sigma_1: Principal stress 1
            sigma_2: Principal stress 2
            sigma_3: Principal stress 3 (default: 0)
            
        Returns:
            von Mises stress
        """
        return math.sqrt(
            0.5 * (
                (sigma_1 - sigma_2)**2 + 
                (sigma_2 - sigma_3)**2 + 
                (sigma_3 - sigma_1)**2
            )
        )
    
    @staticmethod
    def interpolate_material_property(
        temperature: float,
        temp_property_pairs: list,
        property_name: str = "property"
    ) -> float:
        """
        Interpolate material property based on temperature.
        
        Args:
            temperature: Target temperature
            temp_property_pairs: List of (temperature, property) tuples
            property_name: Name of property for error messages
            
        Returns:
            Interpolated property value
        """
        if not temp_property_pairs:
            raise ValueError("Temperature-property pairs cannot be empty")
        
        # Sort by temperature
        sorted_pairs = sorted(temp_property_pairs, key=lambda x: x[0])
        
        # Check if temperature is within range
        min_temp = sorted_pairs[0][0]
        max_temp = sorted_pairs[-1][0]
        
        if temperature < min_temp or temperature > max_temp:
            raise ValueError(
                f"Temperature {temperature} is outside the range "
                f"[{min_temp}, {max_temp}] for {property_name}"
            )
        
        # Find surrounding points
        for i in range(len(sorted_pairs) - 1):
            temp1, prop1 = sorted_pairs[i]
            temp2, prop2 = sorted_pairs[i + 1]
            
            if temp1 <= temperature <= temp2:
                # Linear interpolation
                ratio = (temperature - temp1) / (temp2 - temp1)
                return prop1 + ratio * (prop2 - prop1)
        
        # If exact match
        for temp, prop in sorted_pairs:
            if temp == temperature:
                return prop
        
        raise ValueError(f"Unable to interpolate {property_name} at temperature {temperature}")
    
    @staticmethod
    def validate_engineering_parameters(
        parameters: Dict[str, Any],
        parameter_rules: Dict[str, Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Validate engineering parameters against defined rules.
        
        Args:
            parameters: Dictionary of parameters to validate
            parameter_rules: Validation rules for each parameter
            
        Returns:
            Dictionary with validation results
        """
        errors = []
        warnings = []
        
        for param_name, rules in parameter_rules.items():
            if param_name not in parameters:
                if rules.get("required", False):
                    errors.append(f"Required parameter '{param_name}' is missing")
                continue
            
            value = parameters[param_name]
            
            # Type validation
            expected_type = rules.get("type")
            if expected_type and not isinstance(value, expected_type):
                errors.append(f"Parameter '{param_name}' must be of type {expected_type.__name__}")
                continue
            
            # Range validation
            if "min_value" in rules and value < rules["min_value"]:
                errors.append(f"Parameter '{param_name}' must be >= {rules['min_value']}")
            
            if "max_value" in rules and value > rules["max_value"]:
                errors.append(f"Parameter '{param_name}' must be <= {rules['max_value']}")
            
            # Warning thresholds
            if "warning_min" in rules and value < rules["warning_min"]:
                warnings.append(f"Parameter '{param_name}' is below recommended minimum of {rules['warning_min']}")
            
            if "warning_max" in rules and value > rules["warning_max"]:
                warnings.append(f"Parameter '{param_name}' is above recommended maximum of {rules['warning_max']}")
        
        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings
        }


class EngineeringConstants:
    """Common engineering constants and material properties."""
    
    # Physical constants
    GRAVITY = 9.80665  # m/s²
    ATMOSPHERIC_PRESSURE = 101325  # Pa
    
    # Material properties (typical values)
    STEEL_ELASTIC_MODULUS = 200e9  # Pa
    STEEL_POISSON_RATIO = 0.3
    STEEL_DENSITY = 7850  # kg/m³
    
    ALUMINUM_ELASTIC_MODULUS = 70e9  # Pa
    ALUMINUM_POISSON_RATIO = 0.33
    ALUMINUM_DENSITY = 2700  # kg/m³
    
    # Engineering factors
    TYPICAL_SAFETY_FACTORS = {
        "static_loading": 2.0,
        "dynamic_loading": 4.0,
        "brittle_materials": 8.0,
        "pressure_vessels": 4.0,
        "aircraft": 1.5
    }
    
    # Pressure vessel codes allowable stress factors
    ASME_STRESS_FACTORS = {
        "tensile_ultimate": 1/3.5,  # UTS/3.5
        "yield_strength": 2/3,      # 2/3 * Yield
        "creep_rupture": 1/1.5      # Creep strength/1.5
    }
