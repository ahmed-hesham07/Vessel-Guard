"""
Calculation engine tests for engineering calculations.

Tests for ASME pressure vessel calculations, pipe stress analysis,
and other engineering calculations.
"""

import pytest
import math
from typing import Dict, Any

from app.services.calculation_engine import (
    PressureVesselCalculator,
    ASMEVIIICalculator,
    PipeStressCalculator,
    MaterialPropertyCalculator,
    SafetyFactorCalculator,
    CalculationError,
    ValidationError
)
from app.db.models.material import Material, MaterialType, MaterialStandard
from app.db.models.vessel import Vessel


class TestPressureVesselCalculator:
    """Test pressure vessel calculation functions."""
    
    def test_cylindrical_shell_thickness_calculation(self):
        """Test ASME VIII cylindrical shell thickness calculation."""
        calculator = ASMEVIIICalculator()
        
        # Test case: Standard pressure vessel
        inputs = {
            'design_pressure': 150.0,  # psi
            'inside_radius': 24.0,  # inches
            'allowable_stress': 20000.0,  # psi
            'joint_efficiency': 1.0,
            'corrosion_allowance': 0.125  # inches
        }
        
        result = calculator.calculate_cylindrical_shell_thickness(inputs)
        
        # Expected: t = (P * R) / (S * E - 0.6 * P) + CA
        # t = (150 * 24) / (20000 * 1.0 - 0.6 * 150) + 0.125
        # t = 3600 / (20000 - 90) + 0.125 = 3600 / 19910 + 0.125 ≈ 0.306 inches
        
        assert result['required_thickness'] == pytest.approx(0.181, rel=1e-2)
        assert result['minimum_thickness'] == pytest.approx(0.306, rel=1e-2)
        assert result['governing_calculation'] == 'ASME VIII Div 1 - UG-27'
        assert result['safety_factor'] > 1.0
    
    def test_spherical_shell_thickness_calculation(self):
        """Test ASME VIII spherical shell thickness calculation."""
        calculator = ASMEVIIICalculator()
        
        inputs = {
            'design_pressure': 200.0,  # psi
            'inside_radius': 30.0,  # inches
            'allowable_stress': 20000.0,  # psi
            'joint_efficiency': 0.85,
            'corrosion_allowance': 0.125  # inches
        }
        
        result = calculator.calculate_spherical_shell_thickness(inputs)
        
        # Expected: t = (P * R) / (2 * S * E - 0.2 * P) + CA
        # t = (200 * 30) / (2 * 20000 * 0.85 - 0.2 * 200) + 0.125
        # t = 6000 / (34000 - 40) + 0.125 = 6000 / 33960 + 0.125 ≈ 0.302 inches
        
        assert result['required_thickness'] == pytest.approx(0.177, rel=1e-2)
        assert result['minimum_thickness'] == pytest.approx(0.302, rel=1e-2)
        assert result['governing_calculation'] == 'ASME VIII Div 1 - UG-27'
    
    def test_ellipsoidal_head_thickness_calculation(self):
        """Test ASME VIII ellipsoidal head thickness calculation."""
        calculator = ASMEVIIICalculator()
        
        inputs = {
            'design_pressure': 150.0,  # psi
            'inside_diameter': 48.0,  # inches
            'allowable_stress': 20000.0,  # psi
            'joint_efficiency': 1.0,
            'head_type': 'ellipsoidal',
            'aspect_ratio': 2.0,  # 2:1 ellipsoidal head
            'corrosion_allowance': 0.125  # inches
        }
        
        result = calculator.calculate_head_thickness(inputs)
        
        # For 2:1 ellipsoidal head: K = 1.0
        # t = (P * D * K) / (2 * S * E - 0.2 * P) + CA
        
        assert result['required_thickness'] > 0
        assert result['minimum_thickness'] > result['required_thickness']
        assert result['head_factor'] == 1.0  # For 2:1 ellipsoidal
        assert 'governing_calculation' in result
    
    def test_torispherical_head_thickness_calculation(self):
        """Test ASME VIII torispherical head thickness calculation."""
        calculator = ASMEVIIICalculator()
        
        inputs = {
            'design_pressure': 150.0,  # psi
            'inside_diameter': 48.0,  # inches
            'allowable_stress': 20000.0,  # psi
            'joint_efficiency': 1.0,
            'head_type': 'torispherical',
            'crown_radius': 48.0,  # inches
            'knuckle_radius': 2.88,  # inches (6% of diameter)
            'corrosion_allowance': 0.125  # inches
        }
        
        result = calculator.calculate_head_thickness(inputs)
        
        assert result['required_thickness'] > 0
        assert result['minimum_thickness'] > result['required_thickness']
        assert result['head_factor'] > 1.0  # Torispherical factor > 1.0
        assert 'crown_radius_ratio' in result
        assert 'knuckle_radius_ratio' in result
    
    def test_external_pressure_calculation(self):
        """Test external pressure calculation per ASME VIII."""
        calculator = ASMEVIIICalculator()
        
        inputs = {
            'external_pressure': 15.0,  # psi (vacuum)
            'outside_diameter': 49.0,  # inches
            'length': 120.0,  # inches
            'thickness': 0.25,  # inches
            'modulus_of_elasticity': 29000000.0,  # psi
            'yield_strength': 38000.0  # psi
        }
        
        result = calculator.calculate_external_pressure_resistance(inputs)
        
        assert result['allowable_external_pressure'] > 0
        assert result['do_over_t_ratio'] == pytest.approx(196.0, rel=1e-2)
        assert result['l_over_do_ratio'] == pytest.approx(2.45, rel=1e-2)
        assert 'chart_used' in result
        assert result['is_adequate'] is not None
    
    def test_nozzle_reinforcement_calculation(self):
        """Test nozzle reinforcement calculation."""
        calculator = ASMEVIIICalculator()
        
        inputs = {
            'vessel_diameter': 48.0,  # inches
            'vessel_thickness': 0.375,  # inches
            'nozzle_diameter': 8.0,  # inches
            'nozzle_thickness': 0.322,  # inches
            'design_pressure': 150.0,  # psi
            'allowable_stress_vessel': 20000.0,  # psi
            'allowable_stress_nozzle': 20000.0,  # psi
            'joint_efficiency': 1.0,
            'corrosion_allowance': 0.125  # inches
        }
        
        result = calculator.calculate_nozzle_reinforcement(inputs)
        
        assert result['area_required'] > 0
        assert result['area_available'] > 0
        assert result['reinforcement_ratio'] > 0
        assert 'is_adequate' in result
        assert 'reinforcement_pad_required' in result
    
    def test_wind_load_calculation(self):
        """Test wind load calculation on vessels."""
        calculator = PressureVesselCalculator()
        
        inputs = {
            'vessel_diameter': 48.0,  # inches
            'vessel_height': 120.0,  # inches
            'wind_velocity': 90.0,  # mph
            'exposure_category': 'C',
            'importance_factor': 1.0,
            'gust_factor': 0.85,
            'shape_factor': 0.8  # cylindrical vessel
        }
        
        result = calculator.calculate_wind_load(inputs)
        
        assert result['wind_pressure'] > 0
        assert result['total_wind_force'] > 0
        assert result['overturning_moment'] > 0
        assert result['base_shear'] > 0
    
    def test_seismic_load_calculation(self):
        """Test seismic load calculation."""
        calculator = PressureVesselCalculator()
        
        inputs = {
            'vessel_weight': 50000.0,  # lbs
            'vessel_height': 120.0,  # inches
            'seismic_acceleration': 0.2,  # g
            'importance_factor': 1.25,
            'response_modification_factor': 3.0,
            'site_class': 'D'
        }
        
        result = calculator.calculate_seismic_load(inputs)
        
        assert result['base_shear'] > 0
        assert result['overturning_moment'] > 0
        assert result['seismic_force'] > 0


class TestMaterialPropertyCalculator:
    """Test material property calculations."""
    
    def test_allowable_stress_calculation(self):
        """Test allowable stress calculation per ASME VIII."""
        calculator = MaterialPropertyCalculator()
        
        inputs = {
            'yield_strength': 38000.0,  # psi
            'tensile_strength': 70000.0,  # psi
            'temperature': 300.0,  # °F
            'material_type': 'carbon_steel',
            'design_code': 'ASME VIII Div 1'
        }
        
        result = calculator.calculate_allowable_stress(inputs)
        
        # ASME VIII allowable stress = min(Sy/1.5, Su/3.5)
        expected_sy_based = 38000.0 / 1.5  # 25,333 psi
        expected_su_based = 70000.0 / 3.5  # 20,000 psi
        expected_allowable = min(expected_sy_based, expected_su_based)
        
        assert result['allowable_stress'] == pytest.approx(expected_allowable, rel=1e-2)
        assert result['governing_criteria'] == 'tensile_strength'
        assert result['safety_factor_used'] == 3.5
    
    def test_joint_efficiency_determination(self):
        """Test joint efficiency determination."""
        calculator = MaterialPropertyCalculator()
        
        # Test different joint types
        test_cases = [
            {'joint_type': 'butt_joint_full_radiography', 'expected': 1.0},
            {'joint_type': 'butt_joint_spot_radiography', 'expected': 0.85},
            {'joint_type': 'lap_joint_full_radiography', 'expected': 0.75},
            {'joint_type': 'lap_joint_no_radiography', 'expected': 0.60}
        ]
        
        for case in test_cases:
            result = calculator.determine_joint_efficiency({
                'joint_type': case['joint_type'],
                'radiography_type': 'full' if 'full' in case['joint_type'] else 'spot'
            })
            
            assert result['joint_efficiency'] == case['expected']
    
    def test_temperature_derating_factors(self):
        """Test temperature derating factors for materials."""
        calculator = MaterialPropertyCalculator()
        
        inputs = {
            'material_specification': 'SA-516 Grade 70',
            'base_allowable_stress': 20000.0,  # psi at room temperature
            'operating_temperature': 600.0  # °F
        }
        
        result = calculator.apply_temperature_derating(inputs)
        
        # At elevated temperature, allowable stress should be reduced
        assert result['derated_allowable_stress'] < inputs['base_allowable_stress']
        assert result['derating_factor'] < 1.0
        assert result['temperature_limit_check'] is not None


class TestPipeStressCalculator:
    """Test pipe stress analysis calculations."""
    
    def test_thermal_expansion_calculation(self):
        """Test thermal expansion calculation for piping."""
        calculator = PipeStressCalculator()
        
        inputs = {
            'pipe_length': 100.0,  # feet
            'material_expansion_coefficient': 6.5e-6,  # in/in/°F
            'temperature_difference': 250.0,  # °F
            'pipe_diameter': 6.0,  # inches
            'wall_thickness': 0.280  # inches
        }
        
        result = calculator.calculate_thermal_expansion(inputs)
        
        # Expected expansion = L * α * ΔT
        expected_expansion = 100.0 * 12.0 * 6.5e-6 * 250.0  # inches
        
        assert result['total_expansion'] == pytest.approx(expected_expansion, rel=1e-2)
        assert result['expansion_stress'] > 0
        assert result['flexibility_required'] is not None
    
    def test_pressure_stress_calculation(self):
        """Test pressure stress in pipes per ASME B31.3."""
        calculator = PipeStressCalculator()
        
        inputs = {
            'internal_pressure': 300.0,  # psi
            'outside_diameter': 6.625,  # inches
            'wall_thickness': 0.280,  # inches
            'allowable_stress': 20000.0,  # psi
            'joint_efficiency': 1.0,
            'temperature_derating': 1.0
        }
        
        result = calculator.calculate_pressure_stress(inputs)
        
        # Hoop stress = (P * D) / (2 * t)
        expected_hoop_stress = (300.0 * 6.625) / (2.0 * 0.280)
        
        assert result['hoop_stress'] == pytest.approx(expected_hoop_stress, rel=1e-2)
        assert result['longitudinal_stress'] == pytest.approx(expected_hoop_stress / 2.0, rel=1e-2)
        assert result['is_adequate'] is not None
    
    def test_pipe_support_spacing(self):
        """Test pipe support spacing calculation."""
        calculator = PipeStressCalculator()
        
        inputs = {
            'pipe_diameter': 6.625,  # inches
            'wall_thickness': 0.280,  # inches
            'pipe_material_density': 0.284,  # lb/in³
            'fluid_density': 0.036,  # lb/in³ (water)
            'allowable_stress': 20000.0,  # psi
            'safety_factor': 4.0,
            'insulation_weight': 2.0  # lb/ft
        }
        
        result = calculator.calculate_support_spacing(inputs)
        
        assert result['maximum_spacing'] > 0
        assert result['pipe_weight_per_foot'] > 0
        assert result['total_weight_per_foot'] > 0
        assert result['recommended_spacing'] <= result['maximum_spacing']


class TestSafetyFactorCalculator:
    """Test safety factor calculations."""
    
    def test_pressure_vessel_safety_factors(self):
        """Test safety factor calculations for pressure vessels."""
        calculator = SafetyFactorCalculator()
        
        inputs = {
            'design_pressure': 150.0,  # psi
            'test_pressure': 225.0,  # psi (1.5 times design)
            'operating_pressure': 125.0,  # psi
            'burst_pressure': 600.0,  # psi (estimated)
            'yield_pressure': 450.0,  # psi (estimated)
            'application_type': 'pressure_vessel'
        }
        
        result = calculator.calculate_safety_factors(inputs)
        
        assert result['safety_factor_burst'] == pytest.approx(4.8, rel=1e-2)  # 600/125
        assert result['safety_factor_yield'] == pytest.approx(3.6, rel=1e-2)  # 450/125
        assert result['test_factor'] == pytest.approx(1.8, rel=1e-2)  # 225/125
        assert result['meets_asme_requirements'] is not None
    
    def test_fatigue_analysis(self):
        """Test fatigue analysis calculations."""
        calculator = SafetyFactorCalculator()
        
        inputs = {
            'stress_amplitude': 5000.0,  # psi
            'mean_stress': 10000.0,  # psi
            'material_endurance_limit': 15000.0,  # psi
            'surface_finish_factor': 0.85,
            'size_factor': 0.9,
            'reliability_factor': 0.9,
            'temperature_factor': 1.0,
            'stress_concentration_factor': 2.0
        }
        
        result = calculator.calculate_fatigue_life(inputs)
        
        assert result['corrected_endurance_limit'] > 0
        assert result['safety_factor_fatigue'] > 0
        assert result['estimated_cycles'] > 0


class TestCalculationValidation:
    """Test calculation input validation and error handling."""
    
    def test_invalid_pressure_input(self):
        """Test validation of pressure inputs."""
        calculator = ASMEVIIICalculator()
        
        # Negative pressure should raise validation error
        with pytest.raises(ValidationError):
            calculator.calculate_cylindrical_shell_thickness({
                'design_pressure': -50.0,  # Invalid negative pressure
                'inside_radius': 24.0,
                'allowable_stress': 20000.0,
                'joint_efficiency': 1.0,
                'corrosion_allowance': 0.125
            })
    
    def test_invalid_geometry_input(self):
        """Test validation of geometry inputs."""
        calculator = ASMEVIIICalculator()
        
        # Zero radius should raise validation error
        with pytest.raises(ValidationError):
            calculator.calculate_cylindrical_shell_thickness({
                'design_pressure': 150.0,
                'inside_radius': 0.0,  # Invalid zero radius
                'allowable_stress': 20000.0,
                'joint_efficiency': 1.0,
                'corrosion_allowance': 0.125
            })
    
    def test_invalid_material_properties(self):
        """Test validation of material properties."""
        calculator = MaterialPropertyCalculator()
        
        # Negative allowable stress should raise validation error
        with pytest.raises(ValidationError):
            calculator.calculate_allowable_stress({
                'yield_strength': -1000.0,  # Invalid negative strength
                'tensile_strength': 70000.0,
                'temperature': 300.0,
                'material_type': 'carbon_steel',
                'design_code': 'ASME VIII Div 1'
            })
    
    def test_calculation_error_handling(self):
        """Test calculation error handling."""
        calculator = ASMEVIIICalculator()
        
        # Division by zero scenario (very low allowable stress)
        with pytest.raises(CalculationError):
            calculator.calculate_cylindrical_shell_thickness({
                'design_pressure': 150.0,
                'inside_radius': 24.0,
                'allowable_stress': 0.1,  # Extremely low allowable stress
                'joint_efficiency': 1.0,
                'corrosion_allowance': 0.125
            })
    
    def test_unit_conversion_validation(self):
        """Test unit conversion and validation."""
        calculator = PressureVesselCalculator()
        
        # Test unit conversion
        result = calculator.convert_units({
            'pressure': 10.0,
            'from_unit': 'bar',
            'to_unit': 'psi'
        })
        
        assert result['converted_value'] == pytest.approx(145.0, rel=1e-2)
        
        # Test invalid unit
        with pytest.raises(ValidationError):
            calculator.convert_units({
                'pressure': 10.0,
                'from_unit': 'invalid_unit',
                'to_unit': 'psi'
            })


class TestComplexCalculationScenarios:
    """Test complex, multi-step calculation scenarios."""
    
    def test_complete_pressure_vessel_design(self):
        """Test complete pressure vessel design calculation."""
        calculator = ASMEVIIICalculator()
        
        # Design inputs
        design_inputs = {
            'design_pressure': 150.0,  # psi
            'design_temperature': 350.0,  # °F
            'inside_diameter': 48.0,  # inches
            'overall_length': 120.0,  # inches
            'head_type': 'ellipsoidal',
            'material_spec': 'SA-516 Grade 70',
            'joint_efficiency': 1.0,
            'corrosion_allowance': 0.125,
            'wind_velocity': 90.0,  # mph
            'seismic_zone': 3
        }
        
        # Perform complete design calculation
        result = calculator.complete_vessel_design(design_inputs)
        
        # Verify all components calculated
        assert 'shell_thickness' in result
        assert 'head_thickness' in result
        assert 'nozzle_calculations' in result
        assert 'wind_loads' in result
        assert 'seismic_loads' in result
        assert 'weight_calculations' in result
        assert 'code_compliance_check' in result
        
        # Verify design adequacy
        assert result['design_adequate'] is not None
        assert result['governing_criteria'] is not None
        assert result['safety_margins'] is not None
    
    def test_fitness_for_service_assessment(self):
        """Test fitness-for-service assessment per API 579."""
        calculator = PressureVesselCalculator()
        
        # Assessment inputs
        inputs = {
            'original_thickness': 0.375,  # inches
            'current_thickness': 0.250,  # inches
            'corrosion_rate': 0.005,  # inches/year
            'operating_pressure': 125.0,  # psi
            'design_pressure': 150.0,  # psi
            'allowable_stress': 20000.0,  # psi
            'remaining_life_required': 10.0,  # years
            'inspection_confidence': 'high'
        }
        
        result = calculator.assess_fitness_for_service(inputs)
        
        assert result['remaining_life'] >= 0
        assert result['minimum_thickness'] > 0
        assert result['fitness_rating'] in ['fit', 'monitor', 'repair', 'replace']
        assert result['next_inspection_date'] is not None
        assert result['recommended_actions'] is not None
