"""
Base calculation engine for engineering calculations.

This module provides the foundation for all engineering calculations
including ASME pressure vessel calculations, pipe stress analysis,
and material property calculations.
"""

from typing import Dict, Any, List, Optional
from abc import ABC, abstractmethod
import math
from enum import Enum

from app.core.exceptions import ValidationError, CalculationError


class CalculationType(str, Enum):
    """Types of calculations supported."""
    PRESSURE_VESSEL_THICKNESS = "pressure_vessel_thickness"
    EXTERNAL_PRESSURE = "external_pressure"
    NOZZLE_REINFORCEMENT = "nozzle_reinforcement"
    HEAD_THICKNESS = "head_thickness"
    PIPE_STRESS = "pipe_stress"
    THERMAL_EXPANSION = "thermal_expansion"
    WIND_LOAD = "wind_load"
    SEISMIC_LOAD = "seismic_load"
    MATERIAL_PROPERTIES = "material_properties"


class BaseCalculator(ABC):
    """Base class for all calculation engines."""
    
    def __init__(self):
        self.calculation_type = None
        self.last_result = None
    
    @abstractmethod
    def validate_inputs(self, inputs: Dict[str, Any]) -> bool:
        """Validate calculation inputs."""
        pass
    
    @abstractmethod
    def calculate(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Perform the calculation."""
        pass
    
    def convert_units(self, value: float, from_unit: str, to_unit: str, unit_type: str = "pressure") -> float:
        """Convert between different unit systems."""
        conversions = {
            "pressure": {
                ("psi", "bar"): 0.0689476,
                ("bar", "psi"): 14.5038,
                ("psi", "mpa"): 0.00689476,
                ("mpa", "psi"): 145.038,
                ("bar", "mpa"): 0.1,
                ("mpa", "bar"): 10.0
            },
            "length": {
                ("in", "mm"): 25.4,
                ("mm", "in"): 0.0393701,
                ("ft", "m"): 0.3048,
                ("m", "ft"): 3.28084
            },
            "temperature": {
                ("f", "c"): lambda f: (f - 32) * 5/9,
                ("c", "f"): lambda c: c * 9/5 + 32,
                ("f", "k"): lambda f: (f - 32) * 5/9 + 273.15,
                ("k", "f"): lambda k: (k - 273.15) * 9/5 + 32
            }
        }
        
        key = (from_unit.lower(), to_unit.lower())
        if unit_type in conversions and key in conversions[unit_type]:
            factor = conversions[unit_type][key]
            if callable(factor):
                return factor(value)
            return value * factor
        else:
            raise ValidationError(f"Unsupported unit conversion: {from_unit} to {to_unit}")


class ASMEVIIICalculator(BaseCalculator):
    """ASME Section VIII pressure vessel calculations."""
    
    def __init__(self):
        super().__init__()
        self.calculation_type = "ASME VIII"
    
    def validate_inputs(self, inputs: Dict[str, Any]) -> bool:
        """Validate ASME VIII calculation inputs."""
        required_fields = ["design_pressure", "allowable_stress"]
        
        for field in required_fields:
            if field not in inputs:
                raise ValidationError(f"Missing required field: {field}")
            
            if not isinstance(inputs[field], (int, float)) or inputs[field] <= 0:
                raise ValidationError(f"{field} must be a positive number")
        
        return True
    
    def calculate_cylindrical_shell_thickness(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate required thickness for cylindrical shell per UG-27."""
        self.validate_inputs(inputs)
        
        P = inputs["design_pressure"]  # psi
        R = inputs.get("inside_radius", inputs.get("inside_diameter", 0) / 2)  # inches
        S = inputs["allowable_stress"]  # psi
        E = inputs.get("joint_efficiency", 1.0)
        CA = inputs.get("corrosion_allowance", 0.125)  # inches
        
        if R <= 0:
            raise ValidationError("Inside radius/diameter must be positive")
        
        # ASME VIII Div 1 formula: t = (P * R) / (S * E - 0.6 * P)
        denominator = S * E - 0.6 * P
        if denominator <= 0:
            raise CalculationError("Invalid stress conditions - denominator <= 0")
        
        t_required = (P * R) / denominator
        t_minimum = t_required + CA
        
        # Safety factor calculation
        safety_factor = (S * E) / (P * (R / t_required + 0.6))
        
        return {
            "required_thickness": round(t_required, 4),
            "minimum_thickness": round(t_minimum, 4),
            "safety_factor": round(safety_factor, 2),
            "governing_calculation": "ASME VIII Div 1 - UG-27",
            "code_allowable_stress": S,
            "joint_efficiency_used": E,
            "design_pressure": P,
            "inside_radius": R
        }
    
    def calculate_spherical_shell_thickness(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate required thickness for spherical shell per UG-27."""
        self.validate_inputs(inputs)
        
        P = inputs["design_pressure"]  # psi
        R = inputs.get("inside_radius", inputs.get("inside_diameter", 0) / 2)  # inches
        S = inputs["allowable_stress"]  # psi
        E = inputs.get("joint_efficiency", 1.0)
        CA = inputs.get("corrosion_allowance", 0.125)  # inches
        
        # ASME VIII Div 1 formula: t = (P * R) / (2 * S * E - 0.2 * P)
        denominator = 2 * S * E - 0.2 * P
        if denominator <= 0:
            raise CalculationError("Invalid stress conditions - denominator <= 0")
        
        t_required = (P * R) / denominator
        t_minimum = t_required + CA
        
        # Safety factor calculation
        safety_factor = (2 * S * E) / (P * (R / t_required + 0.2))
        
        return {
            "required_thickness": round(t_required, 4),
            "minimum_thickness": round(t_minimum, 4),
            "safety_factor": round(safety_factor, 2),
            "governing_calculation": "ASME VIII Div 1 - UG-27",
            "code_allowable_stress": S,
            "joint_efficiency_used": E
        }
    
    def calculate_head_thickness(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate required thickness for vessel heads."""
        self.validate_inputs(inputs)
        
        P = inputs["design_pressure"]  # psi
        D = inputs.get("inside_diameter", inputs.get("inside_radius", 0) * 2)  # inches
        S = inputs["allowable_stress"]  # psi
        E = inputs.get("joint_efficiency", 1.0)
        CA = inputs.get("corrosion_allowance", 0.125)  # inches
        head_type = inputs.get("head_type", "ellipsoidal")
        
        # Determine head factor K based on head type
        if head_type == "ellipsoidal":
            aspect_ratio = inputs.get("aspect_ratio", 2.0)  # 2:1 ellipsoidal
            if aspect_ratio == 2.0:
                K = 1.0
            else:
                K = max(1.0, aspect_ratio / 2.0)  # Simplified approximation
        elif head_type == "torispherical":
            crown_radius = inputs.get("crown_radius", D)
            knuckle_radius = inputs.get("knuckle_radius", 0.06 * D)
            # Simplified torispherical factor calculation
            K = 0.885 / (1 + knuckle_radius / crown_radius)
        elif head_type == "hemispherical":
            K = 0.5  # Hemispherical head factor
        else:
            K = 1.0  # Default to ellipsoidal
        
        # Calculate thickness: t = (P * D * K) / (2 * S * E - 0.2 * P)
        denominator = 2 * S * E - 0.2 * P
        if denominator <= 0:
            raise CalculationError("Invalid stress conditions - denominator <= 0")
        
        t_required = (P * D * K) / denominator
        t_minimum = t_required + CA
        
        return {
            "required_thickness": round(t_required, 4),
            "minimum_thickness": round(t_minimum, 4),
            "head_factor": K,
            "head_type": head_type,
            "governing_calculation": f"ASME VIII Div 1 - {head_type} head",
            "design_pressure": P,
            "inside_diameter": D
        }
    
    def calculate_external_pressure_resistance(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate allowable external pressure per UG-28."""
        Do = inputs["outside_diameter"]  # inches
        L = inputs["length"]  # inches
        t = inputs["thickness"]  # inches
        E_mod = inputs["modulus_of_elasticity"]  # psi
        Sy = inputs["yield_strength"]  # psi
        
        # Calculate Do/t ratio
        do_t_ratio = Do / t
        
        # Calculate L/Do ratio
        l_do_ratio = L / Do
        
        # Simplified external pressure calculation
        # This is a basic implementation - full ASME calculations are more complex
        if do_t_ratio < 10:
            # Thick shell
            Pa = 2 * Sy / (3 * do_t_ratio)
        else:
            # Thin shell - use elastic buckling
            Pa = (2.42 * E_mod) / ((do_t_ratio ** 2) * (l_do_ratio + 0.45) ** 0.5)
        
        external_pressure = inputs.get("external_pressure", 0)
        is_adequate = Pa >= external_pressure
        
        return {
            "allowable_external_pressure": round(Pa, 2),
            "do_over_t_ratio": round(do_t_ratio, 2),
            "l_over_do_ratio": round(l_do_ratio, 2),
            "chart_used": "Simplified calculation",
            "is_adequate": is_adequate,
            "safety_factor": round(Pa / max(external_pressure, 1), 2) if external_pressure > 0 else None
        }
    
    def calculate_nozzle_reinforcement(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate nozzle reinforcement requirements per UG-37."""
        D_vessel = inputs["vessel_diameter"]  # inches
        t_vessel = inputs["vessel_thickness"]  # inches
        d_nozzle = inputs["nozzle_diameter"]  # inches
        t_nozzle = inputs["nozzle_thickness"]  # inches
        P = inputs["design_pressure"]  # psi
        S_vessel = inputs["allowable_stress_vessel"]  # psi
        S_nozzle = inputs.get("allowable_stress_nozzle", S_vessel)  # psi
        E = inputs.get("joint_efficiency", 1.0)
        CA = inputs.get("corrosion_allowance", 0.125)  # inches
        
        # Calculate required area of reinforcement
        tr = (P * (D_vessel / 2)) / (S_vessel * E - 0.6 * P)  # Required thickness without nozzle
        A_required = d_nozzle * max(tr, t_vessel) * 2
        
        # Calculate available area of reinforcement
        # Area in vessel wall
        A1 = (D_vessel - d_nozzle) * (t_vessel - tr) * 2
        
        # Area in nozzle wall
        A2 = 2 * t_nozzle * min(2.5 * t_nozzle, 2.5 * t_vessel)
        
        # Total available area (simplified - doesn't include welds)
        A_available = A1 + A2
        
        reinforcement_ratio = A_available / A_required
        is_adequate = reinforcement_ratio >= 1.0
        reinforcement_pad_required = not is_adequate
        
        return {
            "area_required": round(A_required, 3),
            "area_available": round(A_available, 3),
            "reinforcement_ratio": round(reinforcement_ratio, 3),
            "is_adequate": is_adequate,
            "reinforcement_pad_required": reinforcement_pad_required,
            "governing_calculation": "ASME VIII Div 1 - UG-37"
        }
    
    def calculate(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Main calculation dispatcher."""
        calc_type = inputs.get("calculation_type", "cylindrical_shell_thickness")
        
        if calc_type == "cylindrical_shell_thickness":
            return self.calculate_cylindrical_shell_thickness(inputs)
        elif calc_type == "spherical_shell_thickness":
            return self.calculate_spherical_shell_thickness(inputs)
        elif calc_type == "head_thickness":
            return self.calculate_head_thickness(inputs)
        elif calc_type == "external_pressure":
            return self.calculate_external_pressure_resistance(inputs)
        elif calc_type == "nozzle_reinforcement":
            return self.calculate_nozzle_reinforcement(inputs)
        else:
            raise ValidationError(f"Unsupported calculation type: {calc_type}")


class PressureVesselCalculator(BaseCalculator):
    """General pressure vessel calculations."""
    
    def __init__(self):
        super().__init__()
        self.calculation_type = "pressure_vessel"
    
    def validate_inputs(self, inputs: Dict[str, Any]) -> bool:
        """Validate pressure vessel calculation inputs."""
        # Basic validation
        return True
    
    def calculate_wind_load(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate wind loads on pressure vessels."""
        D = inputs["vessel_diameter"] / 12  # Convert to feet
        H = inputs["vessel_height"] / 12  # Convert to feet
        V = inputs["wind_velocity"]  # mph
        Ce = inputs.get("exposure_category_factor", 1.0)
        I = inputs.get("importance_factor", 1.0)
        Gf = inputs.get("gust_factor", 0.85)
        Cf = inputs.get("shape_factor", 0.8)  # For cylindrical vessels
        
        # Calculate design wind pressure: q = 0.00256 * Ce * I * V^2
        q = 0.00256 * Ce * I * (V ** 2)  # psf
        
        # Calculate wind force: F = q * Gf * Cf * A
        A = D * H  # Projected area in ft²
        F = q * Gf * Cf * A  # Total wind force in lbs
        
        # Calculate overturning moment at base
        M = F * (H / 2)  # lb-ft
        
        return {
            "wind_pressure": round(q, 2),
            "total_wind_force": round(F, 0),
            "overturning_moment": round(M, 0),
            "base_shear": round(F, 0),
            "projected_area": round(A, 2)
        }
    
    def calculate_seismic_load(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate seismic loads on pressure vessels."""
        W = inputs["vessel_weight"]  # lbs
        H = inputs["vessel_height"] / 12  # feet
        Cs = inputs["seismic_acceleration"]  # g
        I = inputs.get("importance_factor", 1.25)
        R = inputs.get("response_modification_factor", 3.0)
        
        # Calculate base shear: V = Cs * I * W / R
        V = (Cs * I * W) / R  # lbs
        
        # Calculate overturning moment (simplified)
        M = V * (H * 0.75)  # Assume center of mass at 75% of height
        
        return {
            "base_shear": round(V, 0),
            "overturning_moment": round(M, 0),
            "seismic_force": round(V, 0),
            "design_acceleration": Cs
        }
    
    def assess_fitness_for_service(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Assess fitness for service per API 579."""
        t_original = inputs["original_thickness"]  # inches
        t_current = inputs["current_thickness"]  # inches
        corrosion_rate = inputs["corrosion_rate"]  # inches/year
        P_operating = inputs["operating_pressure"]  # psi
        P_design = inputs["design_pressure"]  # psi
        S_allowable = inputs["allowable_stress"]  # psi
        life_required = inputs["remaining_life_required"]  # years
        
        # Calculate minimum required thickness
        # Simplified - actual API 579 calculations are more complex
        R = inputs.get("inside_radius", 24.0)  # inches
        E = inputs.get("joint_efficiency", 1.0)
        t_min = (P_operating * R) / (S_allowable * E - 0.6 * P_operating)
        
        # Calculate remaining life
        if corrosion_rate > 0:
            remaining_life = (t_current - t_min) / corrosion_rate
        else:
            remaining_life = float('inf')
        
        # Determine fitness rating
        if remaining_life >= life_required and t_current >= t_min:
            fitness_rating = "fit"
        elif remaining_life >= life_required * 0.5:
            fitness_rating = "monitor"
        elif t_current >= t_min:
            fitness_rating = "repair"
        else:
            fitness_rating = "replace"
        
        # Calculate next inspection date (simplified)
        if fitness_rating == "fit":
            next_inspection_interval = min(5, remaining_life / 3)
        elif fitness_rating == "monitor":
            next_inspection_interval = min(2, remaining_life / 5)
        else:
            next_inspection_interval = 1
        
        return {
            "remaining_life": round(remaining_life, 1) if remaining_life != float('inf') else "Indefinite",
            "minimum_thickness": round(t_min, 4),
            "fitness_rating": fitness_rating,
            "next_inspection_date": f"{next_inspection_interval} years",
            "recommended_actions": self._get_fitness_recommendations(fitness_rating),
            "current_safety_factor": round(t_current / t_min, 2) if t_min > 0 else None
        }
    
    def _get_fitness_recommendations(self, rating: str) -> List[str]:
        """Get fitness for service recommendations."""
        recommendations = {
            "fit": ["Continue normal operation", "Follow regular inspection schedule"],
            "monitor": ["Increase inspection frequency", "Monitor corrosion rate", "Consider repair planning"],
            "repair": ["Plan repair or replacement", "Reduce operating pressure if possible", "Immediate inspection required"],
            "replace": ["Immediate replacement required", "Do not operate", "Emergency shutdown recommended"]
        }
        return recommendations.get(rating, ["Consult engineering specialist"])
    
    def calculate(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Main calculation dispatcher."""
        calc_type = inputs.get("calculation_type", "wind_load")
        
        if calc_type == "wind_load":
            return self.calculate_wind_load(inputs)
        elif calc_type == "seismic_load":
            return self.calculate_seismic_load(inputs)
        elif calc_type == "fitness_for_service":
            return self.assess_fitness_for_service(inputs)
        else:
            raise ValidationError(f"Unsupported calculation type: {calc_type}")


class PipeStressCalculator(BaseCalculator):
    """Pipe stress analysis calculations per ASME B31.3."""
    
    def __init__(self):
        super().__init__()
        self.calculation_type = "pipe_stress"
    
    def validate_inputs(self, inputs: Dict[str, Any]) -> bool:
        """Validate pipe stress calculation inputs."""
        return True
    
    def calculate_thermal_expansion(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate thermal expansion in piping systems."""
        L = inputs["pipe_length"] * 12  # Convert feet to inches
        alpha = inputs["material_expansion_coefficient"]  # in/in/°F
        delta_T = inputs["temperature_difference"]  # °F
        
        # Calculate total expansion
        total_expansion = L * alpha * delta_T  # inches
        
        # Calculate expansion stress (simplified)
        E = inputs.get("modulus_of_elasticity", 29000000)  # psi
        expansion_stress = E * alpha * delta_T  # psi
        
        return {
            "total_expansion": round(total_expansion, 4),
            "expansion_stress": round(expansion_stress, 0),
            "flexibility_required": total_expansion > 1.0  # Rule of thumb
        }
    
    def calculate_pressure_stress(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate pressure stress in pipes per ASME B31.3."""
        P = inputs["internal_pressure"]  # psi
        Do = inputs["outside_diameter"]  # inches
        t = inputs["wall_thickness"]  # inches
        S = inputs["allowable_stress"]  # psi
        E = inputs.get("joint_efficiency", 1.0)
        T = inputs.get("temperature_derating", 1.0)
        
        # Calculate hoop stress
        hoop_stress = (P * Do) / (2 * t)  # psi
        
        # Calculate longitudinal stress
        longitudinal_stress = (P * Do) / (4 * t)  # psi
        
        # Check adequacy
        allowable = S * E * T
        is_adequate = hoop_stress <= allowable
        
        return {
            "hoop_stress": round(hoop_stress, 0),
            "longitudinal_stress": round(longitudinal_stress, 0),
            "allowable_stress": round(allowable, 0),
            "is_adequate": is_adequate,
            "safety_factor": round(allowable / hoop_stress, 2) if hoop_stress > 0 else None
        }
    
    def calculate_support_spacing(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate pipe support spacing."""
        Do = inputs["pipe_diameter"]  # inches
        t = inputs["wall_thickness"]  # inches
        rho_pipe = inputs["pipe_material_density"]  # lb/in³
        rho_fluid = inputs["fluid_density"]  # lb/in³
        S_allowable = inputs["allowable_stress"]  # psi
        SF = inputs.get("safety_factor", 4.0)
        
        # Calculate pipe weight per foot
        A_pipe = math.pi * (Do**2 - (Do - 2*t)**2) / 4  # in²
        pipe_weight = A_pipe * rho_pipe * 12  # lb/ft
        
        # Calculate fluid weight per foot
        A_fluid = math.pi * (Do - 2*t)**2 / 4  # in²
        fluid_weight = A_fluid * rho_fluid * 12  # lb/ft
        
        # Total weight
        total_weight = pipe_weight + fluid_weight + inputs.get("insulation_weight", 0)
        
        # Calculate maximum spacing (simplified beam calculation)
        # Assuming simply supported beam with uniform load
        I = math.pi * (Do**4 - (Do - 2*t)**4) / 64  # in⁴
        max_spacing = math.sqrt((8 * S_allowable * I) / (SF * total_weight * Do / 2))
        max_spacing = max_spacing * 12  # Convert to feet
        
        # Recommended spacing (typically 80% of maximum)
        recommended_spacing = max_spacing * 0.8
        
        return {
            "maximum_spacing": round(max_spacing, 1),
            "recommended_spacing": round(recommended_spacing, 1),
            "pipe_weight_per_foot": round(pipe_weight, 2),
            "fluid_weight_per_foot": round(fluid_weight, 2),
            "total_weight_per_foot": round(total_weight, 2)
        }
    
    def calculate(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Main calculation dispatcher."""
        calc_type = inputs.get("calculation_type", "pressure_stress")
        
        if calc_type == "thermal_expansion":
            return self.calculate_thermal_expansion(inputs)
        elif calc_type == "pressure_stress":
            return self.calculate_pressure_stress(inputs)
        elif calc_type == "support_spacing":
            return self.calculate_support_spacing(inputs)
        else:
            raise ValidationError(f"Unsupported calculation type: {calc_type}")


class MaterialPropertyCalculator(BaseCalculator):
    """Material property and allowable stress calculations."""
    
    def __init__(self):
        super().__init__()
        self.calculation_type = "material_properties"
    
    def validate_inputs(self, inputs: Dict[str, Any]) -> bool:
        """Validate material property inputs."""
        return True
    
    def calculate_allowable_stress(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate allowable stress per ASME VIII."""
        Sy = inputs["yield_strength"]  # psi
        Su = inputs["tensile_strength"]  # psi
        temperature = inputs.get("temperature", 70)  # °F
        design_code = inputs.get("design_code", "ASME VIII Div 1")
        
        # ASME VIII Division 1 allowable stress
        if design_code == "ASME VIII Div 1":
            sy_based = Sy / 1.5  # Yield strength basis
            su_based = Su / 3.5  # Tensile strength basis
            allowable_stress = min(sy_based, su_based)
            
            if allowable_stress == sy_based:
                governing_criteria = "yield_strength"
                safety_factor_used = 1.5
            else:
                governing_criteria = "tensile_strength"
                safety_factor_used = 3.5
        else:
            # Default to conservative values
            allowable_stress = min(Sy / 2.0, Su / 4.0)
            governing_criteria = "conservative_default"
            safety_factor_used = 2.0
        
        # Apply temperature derating if needed
        if temperature > 100:
            derating_factor = self._get_temperature_derating_factor(temperature, inputs.get("material_type", "carbon_steel"))
            allowable_stress *= derating_factor
        else:
            derating_factor = 1.0
        
        return {
            "allowable_stress": round(allowable_stress, 0),
            "governing_criteria": governing_criteria,
            "safety_factor_used": safety_factor_used,
            "temperature_derating_factor": round(derating_factor, 3),
            "yield_based_allowable": round(Sy / 1.5, 0),
            "tensile_based_allowable": round(Su / 3.5, 0)
        }
    
    def determine_joint_efficiency(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Determine joint efficiency based on joint type and radiography."""
        joint_type = inputs.get("joint_type", "butt_joint_full_radiography")
        radiography_type = inputs.get("radiography_type", "full")
        
        joint_efficiencies = {
            "butt_joint_full_radiography": 1.0,
            "butt_joint_spot_radiography": 0.85,
            "butt_joint_no_radiography": 0.70,
            "lap_joint_full_radiography": 0.75,
            "lap_joint_spot_radiography": 0.65,
            "lap_joint_no_radiography": 0.60
        }
        
        joint_efficiency = joint_efficiencies.get(joint_type, 0.70)
        
        return {
            "joint_efficiency": joint_efficiency,
            "joint_type": joint_type,
            "radiography_requirement": radiography_type,
            "asme_reference": "Table UW-12"
        }
    
    def apply_temperature_derating(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Apply temperature derating to allowable stress."""
        base_stress = inputs["base_allowable_stress"]  # psi
        temperature = inputs["operating_temperature"]  # °F
        material_spec = inputs.get("material_specification", "SA-516 Grade 70")
        
        derating_factor = self._get_temperature_derating_factor(temperature, material_spec)
        derated_stress = base_stress * derating_factor
        
        # Check temperature limits
        temp_limit = self._get_temperature_limit(material_spec)
        temp_limit_check = temperature <= temp_limit
        
        return {
            "derated_allowable_stress": round(derated_stress, 0),
            "derating_factor": round(derating_factor, 3),
            "operating_temperature": temperature,
            "temperature_limit": temp_limit,
            "temperature_limit_check": temp_limit_check
        }
    
    def _get_temperature_derating_factor(self, temperature: float, material: str) -> float:
        """Get temperature derating factor for material."""
        # Simplified temperature derating - actual ASME tables are more complex
        if temperature <= 100:
            return 1.0
        elif temperature <= 200:
            return 0.98
        elif temperature <= 300:
            return 0.95
        elif temperature <= 400:
            return 0.90
        elif temperature <= 500:
            return 0.85
        elif temperature <= 600:
            return 0.78
        elif temperature <= 700:
            return 0.70
        else:
            return 0.60  # Very conservative for high temperatures
    
    def _get_temperature_limit(self, material_spec: str) -> float:
        """Get maximum allowable temperature for material."""
        temp_limits = {
            "SA-516 Grade 70": 650,  # °F
            "SA-106 Grade B": 800,
            "SA-335 P11": 1050,
            "SA-213 T22": 1100,
            "default": 650
        }
        return temp_limits.get(material_spec, temp_limits["default"])
    
    def calculate(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Main calculation dispatcher."""
        calc_type = inputs.get("calculation_type", "allowable_stress")
        
        if calc_type == "allowable_stress":
            return self.calculate_allowable_stress(inputs)
        elif calc_type == "joint_efficiency":
            return self.determine_joint_efficiency(inputs)
        elif calc_type == "temperature_derating":
            return self.apply_temperature_derating(inputs)
        else:
            raise ValidationError(f"Unsupported calculation type: {calc_type}")


class SafetyFactorCalculator(BaseCalculator):
    """Safety factor and reliability calculations."""
    
    def __init__(self):
        super().__init__()
        self.calculation_type = "safety_factors"
    
    def validate_inputs(self, inputs: Dict[str, Any]) -> bool:
        """Validate safety factor inputs."""
        return True
    
    def calculate_safety_factors(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate various safety factors."""
        design_pressure = inputs["design_pressure"]  # psi
        operating_pressure = inputs["operating_pressure"]  # psi
        burst_pressure = inputs.get("burst_pressure")  # psi
        yield_pressure = inputs.get("yield_pressure")  # psi
        test_pressure = inputs.get("test_pressure")  # psi
        
        results = {}
        
        # Safety factor on burst pressure
        if burst_pressure:
            results["safety_factor_burst"] = round(burst_pressure / operating_pressure, 2)
        
        # Safety factor on yield
        if yield_pressure:
            results["safety_factor_yield"] = round(yield_pressure / operating_pressure, 2)
        
        # Test factor
        if test_pressure:
            results["test_factor"] = round(test_pressure / operating_pressure, 2)
        
        # Design factor
        results["design_factor"] = round(design_pressure / operating_pressure, 2)
        
        # Check ASME requirements
        asme_requirements = True
        if burst_pressure and results["safety_factor_burst"] < 4.0:
            asme_requirements = False
        if yield_pressure and results["safety_factor_yield"] < 1.5:
            asme_requirements = False
        
        results["meets_asme_requirements"] = asme_requirements
        
        return results
    
    def calculate_fatigue_life(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate fatigue life estimation."""
        stress_amplitude = inputs["stress_amplitude"]  # psi
        mean_stress = inputs["mean_stress"]  # psi
        endurance_limit = inputs["material_endurance_limit"]  # psi
        
        # Apply modification factors
        ka = inputs.get("surface_finish_factor", 0.85)
        kb = inputs.get("size_factor", 0.9)
        kc = inputs.get("reliability_factor", 0.9)
        kd = inputs.get("temperature_factor", 1.0)
        kt = inputs.get("stress_concentration_factor", 1.0)
        
        # Corrected endurance limit
        corrected_endurance = endurance_limit * ka * kb * kc * kd
        
        # Effective stress amplitude with stress concentration
        effective_stress = stress_amplitude * kt
        
        # Safety factor
        safety_factor = corrected_endurance / effective_stress
        
        # Estimated cycles (simplified S-N curve)
        if effective_stress <= corrected_endurance:
            estimated_cycles = float('inf')  # Infinite life
        else:
            # Simplified fatigue curve: N = (Se/Sa)^b where b ≈ 3 for steel
            estimated_cycles = (corrected_endurance / effective_stress) ** 3 * 1e6
        
        return {
            "corrected_endurance_limit": round(corrected_endurance, 0),
            "effective_stress_amplitude": round(effective_stress, 0),
            "safety_factor_fatigue": round(safety_factor, 2),
            "estimated_cycles": int(estimated_cycles) if estimated_cycles != float('inf') else "Infinite"
        }
    
    def calculate(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Main calculation dispatcher."""
        calc_type = inputs.get("calculation_type", "safety_factors")
        
        if calc_type == "safety_factors":
            return self.calculate_safety_factors(inputs)
        elif calc_type == "fatigue_life":
            return self.calculate_fatigue_life(inputs)
        else:
            raise ValidationError(f"Unsupported calculation type: {calc_type}")


class ASMEVIIIDiv2Calculator(BaseCalculator):
    """ASME Section VIII Division 2 pressure vessel calculations."""
    
    def __init__(self):
        super().__init__()
        self.calculation_type = "ASME VIII Div 2"
    
    def validate_inputs(self, inputs: Dict[str, Any]) -> bool:
        """Validate ASME VIII Div 2 calculation inputs."""
        required_fields = ["design_pressure", "allowable_stress", "design_temperature"]
        
        for field in required_fields:
            if field not in inputs:
                raise ValidationError(f"Missing required field: {field}")
            
            if not isinstance(inputs[field], (int, float)) or inputs[field] <= 0:
                raise ValidationError(f"{field} must be a positive number")
        
        return True
    
    def calculate_cylindrical_shell_thickness(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate required thickness for cylindrical shell per ASME VIII Div 2."""
        self.validate_inputs(inputs)
        
        P = inputs["design_pressure"]  # psi
        R = inputs.get("inside_radius", inputs.get("inside_diameter", 0) / 2)  # inches
        S = inputs["allowable_stress"]  # psi
        E = inputs.get("joint_efficiency", 1.0)
        CA = inputs.get("corrosion_allowance", 0.125)  # inches
        design_temp = inputs["design_temperature"]  # °F
        
        if R <= 0:
            raise ValidationError("Inside radius/diameter must be positive")
        
        # ASME VIII Div 2 formula: t = (P * R) / (S * E - 0.5 * P)
        # Division 2 uses different factors than Division 1
        denominator = S * E - 0.5 * P
        if denominator <= 0:
            raise CalculationError("Invalid stress conditions - denominator <= 0")
        
        t_required = (P * R) / denominator
        t_minimum = t_required + CA
        
        # Safety factor calculation for Div 2
        safety_factor = (S * E) / (P * (R / t_required + 0.5))
        
        # Check design temperature limits
        temp_check = self._check_temperature_limits(design_temp, inputs.get("material_spec", "SA-516"))
        
        return {
            "required_thickness": round(t_required, 4),
            "minimum_thickness": round(t_minimum, 4),
            "safety_factor": round(safety_factor, 2),
            "governing_calculation": "ASME VIII Div 2 - Design by Analysis",
            "code_allowable_stress": S,
            "joint_efficiency_used": E,
            "design_pressure": P,
            "inside_radius": R,
            "design_temperature": design_temp,
            "temperature_check": temp_check,
            "division": "Division 2"
        }
    
    def calculate_spherical_shell_thickness(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate required thickness for spherical shell per ASME VIII Div 2."""
        self.validate_inputs(inputs)
        
        P = inputs["design_pressure"]  # psi
        R = inputs.get("inside_radius", inputs.get("inside_diameter", 0) / 2)  # inches
        S = inputs["allowable_stress"]  # psi
        E = inputs.get("joint_efficiency", 1.0)
        CA = inputs.get("corrosion_allowance", 0.125)  # inches
        
        # ASME VIII Div 2 formula: t = (P * R) / (2 * S * E - 0.5 * P)
        denominator = 2 * S * E - 0.5 * P
        if denominator <= 0:
            raise CalculationError("Invalid stress conditions - denominator <= 0")
        
        t_required = (P * R) / denominator
        t_minimum = t_required + CA
        
        # Safety factor calculation
        safety_factor = (2 * S * E) / (P * (R / t_required + 0.5))
        
        return {
            "required_thickness": round(t_required, 4),
            "minimum_thickness": round(t_minimum, 4),
            "safety_factor": round(safety_factor, 2),
            "governing_calculation": "ASME VIII Div 2 - Spherical Shell",
            "code_allowable_stress": S,
            "joint_efficiency_used": E,
            "division": "Division 2"
        }
    
    def calculate_fatigue_analysis(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Perform fatigue analysis per ASME VIII Div 2."""
        cycles = inputs["design_cycles"]
        stress_amplitude = inputs["stress_amplitude"]
        material_spec = inputs.get("material_spec", "SA-516")
        
        # Simplified fatigue calculation
        # In practice, this would use detailed S-N curves
        if material_spec.startswith("SA-516"):
            fatigue_strength = 20000  # psi at 10^6 cycles
        else:
            fatigue_strength = 15000  # psi at 10^6 cycles
        
        # Calculate fatigue life
        if stress_amplitude <= fatigue_strength:
            fatigue_life = float('inf')
            fatigue_rating = "acceptable"
        else:
            # Simplified fatigue life calculation
            fatigue_life = (fatigue_strength / stress_amplitude) ** 3 * 1e6
            fatigue_rating = "limited"
        
        return {
            "fatigue_life_cycles": round(fatigue_life, 0) if fatigue_life != float('inf') else "Infinite",
            "fatigue_rating": fatigue_rating,
            "stress_amplitude": stress_amplitude,
            "fatigue_strength": fatigue_strength,
            "design_cycles": cycles,
            "governing_calculation": "ASME VIII Div 2 - Fatigue Analysis"
        }
    
    def _check_temperature_limits(self, temperature: float, material: str) -> Dict[str, Any]:
        """Check temperature limits for material."""
        temp_limits = {
            "SA-516": 650,
            "SA-106": 800,
            "SA-335": 1050,
            "default": 650
        }
        
        limit = temp_limits.get(material, temp_limits["default"])
        is_within_limit = temperature <= limit
        
        return {
            "temperature": temperature,
            "limit": limit,
            "is_within_limit": is_within_limit,
            "material": material
        }
    
    def calculate(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Main calculation dispatcher."""
        calc_type = inputs.get("calculation_type", "cylindrical_shell_thickness")
        
        if calc_type == "cylindrical_shell_thickness":
            return self.calculate_cylindrical_shell_thickness(inputs)
        elif calc_type == "spherical_shell_thickness":
            return self.calculate_spherical_shell_thickness(inputs)
        elif calc_type == "fatigue_analysis":
            return self.calculate_fatigue_analysis(inputs)
        else:
            raise ValidationError(f"Unsupported calculation type: {calc_type}")


class EN13445Calculator(BaseCalculator):
    """EN 13445 pressure vessel calculations."""
    
    def __init__(self):
        super().__init__()
        self.calculation_type = "EN 13445"
    
    def validate_inputs(self, inputs: Dict[str, Any]) -> bool:
        """Validate EN 13445 calculation inputs."""
        required_fields = ["design_pressure", "allowable_stress", "design_temperature"]
        
        for field in required_fields:
            if field not in inputs:
                raise ValidationError(f"Missing required field: {field}")
            
            if not isinstance(inputs[field], (int, float)) or inputs[field] <= 0:
                raise ValidationError(f"{field} must be a positive number")
        
        return True
    
    def calculate_cylindrical_shell_thickness(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate required thickness for cylindrical shell per EN 13445."""
        self.validate_inputs(inputs)
        
        P = inputs["design_pressure"]  # MPa (EN 13445 uses SI units)
        D = inputs.get("inside_diameter", inputs.get("inside_radius", 0) * 2)  # mm
        f = inputs["allowable_stress"]  # MPa
        z = inputs.get("joint_efficiency", 1.0)
        c = inputs.get("corrosion_allowance", 1.0)  # mm
        
        if D <= 0:
            raise ValidationError("Inside diameter must be positive")
        
        # EN 13445 formula: t = (P * D) / (2 * f * z - P) + c
        denominator = 2 * f * z - P
        if denominator <= 0:
            raise CalculationError("Invalid stress conditions - denominator <= 0")
        
        t_required = (P * D) / denominator
        t_minimum = t_required + c
        
        # Safety factor calculation
        safety_factor = (2 * f * z) / (P * (D / t_required + 1))
        
        return {
            "required_thickness_mm": round(t_required, 2),
            "minimum_thickness_mm": round(t_minimum, 2),
            "safety_factor": round(safety_factor, 2),
            "governing_calculation": "EN 13445 - Cylindrical Shell",
            "code_allowable_stress_mpa": f,
            "joint_efficiency_used": z,
            "design_pressure_mpa": P,
            "inside_diameter_mm": D,
            "standard": "EN 13445"
        }
    
    def calculate_spherical_shell_thickness(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate required thickness for spherical shell per EN 13445."""
        self.validate_inputs(inputs)
        
        P = inputs["design_pressure"]  # MPa
        D = inputs.get("inside_diameter", inputs.get("inside_radius", 0) * 2)  # mm
        f = inputs["allowable_stress"]  # MPa
        z = inputs.get("joint_efficiency", 1.0)
        c = inputs.get("corrosion_allowance", 1.0)  # mm
        
        # EN 13445 formula: t = (P * D) / (4 * f * z - P) + c
        denominator = 4 * f * z - P
        if denominator <= 0:
            raise CalculationError("Invalid stress conditions - denominator <= 0")
        
        t_required = (P * D) / denominator
        t_minimum = t_required + c
        
        # Safety factor calculation
        safety_factor = (4 * f * z) / (P * (D / t_required + 1))
        
        return {
            "required_thickness_mm": round(t_required, 2),
            "minimum_thickness_mm": round(t_minimum, 2),
            "safety_factor": round(safety_factor, 2),
            "governing_calculation": "EN 13445 - Spherical Shell",
            "code_allowable_stress_mpa": f,
            "joint_efficiency_used": z,
            "standard": "EN 13445"
        }
    
    def calculate_head_thickness(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate required thickness for vessel heads per EN 13445."""
        self.validate_inputs(inputs)
        
        P = inputs["design_pressure"]  # MPa
        D = inputs.get("inside_diameter", inputs.get("inside_radius", 0) * 2)  # mm
        f = inputs["allowable_stress"]  # MPa
        z = inputs.get("joint_efficiency", 1.0)
        c = inputs.get("corrosion_allowance", 1.0)  # mm
        head_type = inputs.get("head_type", "ellipsoidal")
        
        # EN 13445 head factors
        if head_type == "ellipsoidal":
            beta = 1.0  # For 2:1 ellipsoidal heads
        elif head_type == "torispherical":
            beta = 1.77  # Typical value for torispherical heads
        elif head_type == "hemispherical":
            beta = 0.5
        else:
            beta = 1.0  # Default to ellipsoidal
        
        # EN 13445 formula: t = (P * D * beta) / (2 * f * z - P) + c
        denominator = 2 * f * z - P
        if denominator <= 0:
            raise CalculationError("Invalid stress conditions - denominator <= 0")
        
        t_required = (P * D * beta) / denominator
        t_minimum = t_required + c
        
        return {
            "required_thickness_mm": round(t_required, 2),
            "minimum_thickness_mm": round(t_minimum, 2),
            "head_factor": beta,
            "head_type": head_type,
            "governing_calculation": f"EN 13445 - {head_type} head",
            "standard": "EN 13445"
        }
    
    def calculate(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Main calculation dispatcher."""
        calc_type = inputs.get("calculation_type", "cylindrical_shell_thickness")
        
        if calc_type == "cylindrical_shell_thickness":
            return self.calculate_cylindrical_shell_thickness(inputs)
        elif calc_type == "spherical_shell_thickness":
            return self.calculate_spherical_shell_thickness(inputs)
        elif calc_type == "head_thickness":
            return self.calculate_head_thickness(inputs)
        else:
            raise ValidationError(f"Unsupported calculation type: {calc_type}")


class API579Calculator(BaseCalculator):
    """API 579/ASME FFS-1 fitness-for-service calculations."""
    
    def __init__(self):
        super().__init__()
        self.calculation_type = "API 579"
    
    def validate_inputs(self, inputs: Dict[str, Any]) -> bool:
        """Validate API 579 calculation inputs."""
        required_fields = ["current_thickness", "operating_pressure", "allowable_stress"]
        
        for field in required_fields:
            if field not in inputs:
                raise ValidationError(f"Missing required field: {field}")
            
            if not isinstance(inputs[field], (int, float)) or inputs[field] <= 0:
                raise ValidationError(f"{field} must be a positive number")
        
        return True
    
    def assess_general_metal_loss(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Assess general metal loss per API 579 Level 1."""
        t_original = inputs["original_thickness"]  # inches
        t_current = inputs["current_thickness"]  # inches
        t_min = inputs["minimum_thickness"]  # inches
        P_operating = inputs["operating_pressure"]  # psi
        S_allowable = inputs["allowable_stress"]  # psi
        R = inputs.get("inside_radius", 24.0)  # inches
        E = inputs.get("joint_efficiency", 1.0)
        
        # Calculate remaining thickness ratio
        t_ratio = t_current / t_original
        
        # Calculate minimum required thickness
        t_required = (P_operating * R) / (S_allowable * E - 0.6 * P_operating)
        
        # Calculate remaining life (if corrosion rate provided)
        corrosion_rate = inputs.get("corrosion_rate", 0)  # inches/year
        if corrosion_rate > 0:
            remaining_life = (t_current - t_required) / corrosion_rate
        else:
            remaining_life = float('inf')
        
        # Determine assessment level
        if t_ratio >= 0.9 and t_current >= t_required:
            assessment_level = "Level 1 - Acceptable"
            fitness_rating = "fit"
        elif t_ratio >= 0.8 and t_current >= t_required:
            assessment_level = "Level 1 - Monitor"
            fitness_rating = "monitor"
        elif t_current >= t_required:
            assessment_level = "Level 2 - Detailed Assessment Required"
            fitness_rating = "repair"
        else:
            assessment_level = "Level 2 - Immediate Action Required"
            fitness_rating = "replace"
        
        return {
            "thickness_ratio": round(t_ratio, 3),
            "current_thickness": t_current,
            "minimum_required_thickness": round(t_required, 4),
            "remaining_life_years": round(remaining_life, 1) if remaining_life != float('inf') else "Indefinite",
            "assessment_level": assessment_level,
            "fitness_rating": fitness_rating,
            "governing_calculation": "API 579 - General Metal Loss Assessment"
        }
    
    def assess_local_metal_loss(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Assess local metal loss per API 579 Level 1."""
        t_original = inputs["original_thickness"]  # inches
        t_current = inputs["current_thickness"]  # inches
        defect_length = inputs["defect_length"]  # inches
        defect_width = inputs["defect_width"]  # inches
        vessel_diameter = inputs["vessel_diameter"]  # inches
        P_operating = inputs["operating_pressure"]  # psi
        S_allowable = inputs["allowable_stress"]  # psi
        
        # Calculate defect parameters
        defect_area = defect_length * defect_width
        vessel_area = math.pi * vessel_diameter * t_original
        area_ratio = defect_area / vessel_area
        
        # Calculate minimum required thickness
        R = vessel_diameter / 2
        E = inputs.get("joint_efficiency", 1.0)
        t_required = (P_operating * R) / (S_allowable * E - 0.6 * P_operating)
        
        # Determine assessment level
        if t_current >= t_required and area_ratio <= 0.1:
            assessment_level = "Level 1 - Acceptable"
            fitness_rating = "fit"
        elif t_current >= t_required and area_ratio <= 0.2:
            assessment_level = "Level 1 - Monitor"
            fitness_rating = "monitor"
        else:
            assessment_level = "Level 2 - Detailed Assessment Required"
            fitness_rating = "repair"
        
        return {
            "defect_area_ratio": round(area_ratio, 3),
            "current_thickness": t_current,
            "minimum_required_thickness": round(t_required, 4),
            "assessment_level": assessment_level,
            "fitness_rating": fitness_rating,
            "governing_calculation": "API 579 - Local Metal Loss Assessment"
        }
    
    def assess_pitting_damage(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Assess pitting damage per API 579 Level 1."""
        t_original = inputs["original_thickness"]  # inches
        t_current = inputs["current_thickness"]  # inches
        pit_depth = inputs["pit_depth"]  # inches
        pit_diameter = inputs["pit_diameter"]  # inches
        pit_spacing = inputs["pit_spacing"]  # inches
        
        # Calculate pitting parameters
        pit_ratio = pit_depth / t_original
        spacing_ratio = pit_spacing / pit_diameter
        
        # Determine assessment level
        if pit_ratio <= 0.5 and spacing_ratio >= 3:
            assessment_level = "Level 1 - Acceptable"
            fitness_rating = "fit"
        elif pit_ratio <= 0.7 and spacing_ratio >= 2:
            assessment_level = "Level 1 - Monitor"
            fitness_rating = "monitor"
        else:
            assessment_level = "Level 2 - Detailed Assessment Required"
            fitness_rating = "repair"
        
        return {
            "pit_depth_ratio": round(pit_ratio, 3),
            "spacing_ratio": round(spacing_ratio, 2),
            "assessment_level": assessment_level,
            "fitness_rating": fitness_rating,
            "governing_calculation": "API 579 - Pitting Damage Assessment"
        }
    
    def calculate(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Main calculation dispatcher."""
        calc_type = inputs.get("calculation_type", "general_metal_loss")
        
        if calc_type == "general_metal_loss":
            return self.assess_general_metal_loss(inputs)
        elif calc_type == "local_metal_loss":
            return self.assess_local_metal_loss(inputs)
        elif calc_type == "pitting_damage":
            return self.assess_pitting_damage(inputs)
        else:
            raise ValidationError(f"Unsupported calculation type: {calc_type}")


# Factory function to get appropriate calculator
def get_calculator(calculation_type: str) -> BaseCalculator:
    """Factory function to get the appropriate calculator."""
    calculators = {
        "asme_viii": ASMEVIIICalculator,
        "asme_viii_div2": ASMEVIIIDiv2Calculator,
        "en_13445": EN13445Calculator,
        "api_579": API579Calculator,
        "pressure_vessel": PressureVesselCalculator,
        "pipe_stress": PipeStressCalculator,
        "material_properties": MaterialPropertyCalculator,
        "safety_factors": SafetyFactorCalculator
    }
    
    calculator_class = calculators.get(calculation_type.lower())
    if not calculator_class:
        raise ValidationError(f"Unknown calculator type: {calculation_type}")
    
    return calculator_class()
