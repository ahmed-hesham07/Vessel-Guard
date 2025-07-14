"""
Pydantic schemas for calculations.

Request/response models for pressure vessel engineering calculations
including ASME calculations, stress analysis, and design verification.
"""

from datetime import datetime
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field, validator


# Base calculation schema
class CalculationBase(BaseModel):
    """Base calculation schema with common fields."""
    name: str = Field(..., min_length=1, max_length=200, description="Calculation name")
    description: Optional[str] = Field(None, max_length=1000, description="Calculation description")
    calculation_type: str = Field(..., min_length=1, max_length=50, description="Type of calculation")
    input_parameters: Dict[str, Any] = Field(default_factory=dict, description="Input parameters")
    
    @validator('calculation_type')
    def validate_calculation_type(cls, v):
        """Validate calculation type."""
        allowed_types = [
            "pressure_vessel", "stress_analysis", "fatigue_analysis",
            "thermal_stress", "nozzle_reinforcement", "flange_design",
            "support_design", "seismic_analysis", "wind_load", "other"
        ]
        if v not in allowed_types:
            raise ValueError(f"Calculation type must be one of: {', '.join(allowed_types)}")
        return v


# Create calculation schema
class CalculationCreate(CalculationBase):
    """Schema for creating a new calculation."""
    vessel_id: int = Field(..., gt=0, description="Vessel ID")
    
    @validator('input_parameters')
    def validate_input_parameters(cls, v):
        """Validate input parameters based on calculation type."""
        # Basic validation - could be expanded based on calculation type
        if not isinstance(v, dict):
            raise ValueError("Input parameters must be a dictionary")
        return v


# Update calculation schema
class CalculationUpdate(BaseModel):
    """Schema for updating calculation."""
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    input_parameters: Optional[Dict[str, Any]] = Field(None)
    output_parameters: Optional[Dict[str, Any]] = Field(None)
    status: Optional[str] = Field(None)
    error_message: Optional[str] = Field(None)
    review_notes: Optional[str] = Field(None, max_length=2000)
    
    @validator('status')
    def validate_status(cls, v):
        """Validate calculation status."""
        if v is not None:
            allowed_statuses = ["pending", "running", "completed", "failed"]
            if v not in allowed_statuses:
                raise ValueError(f"Status must be one of: {', '.join(allowed_statuses)}")
        return v


# Calculation response schema
class Calculation(CalculationBase):
    """Full calculation schema for responses."""
    id: int
    vessel_id: int
    output_parameters: Optional[Dict[str, Any]] = None
    status: str = Field(default="pending")
    error_message: Optional[str] = None
    created_by_id: int
    reviewed_by_id: Optional[int] = None
    reviewed_at: Optional[datetime] = None
    review_notes: Optional[str] = None
    completed_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    is_active: bool

    class Config:
        from_attributes = True


# Calculation summary schema
class CalculationSummary(BaseModel):
    """Summary schema for calculation lists."""
    id: int
    name: str
    calculation_type: str
    status: str
    vessel_id: int
    created_at: datetime
    completed_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# Calculation with vessel info
class CalculationWithVessel(Calculation):
    """Calculation with vessel information."""
    vessel_tag_number: Optional[str] = None
    vessel_name: Optional[str] = None


# Calculation list schema
class CalculationList(BaseModel):
    """Schema for paginated calculation lists."""
    items: List[Calculation]
    total: int = Field(..., ge=0)
    page: int = Field(..., ge=1)
    per_page: int = Field(..., ge=1)
    pages: int = Field(..., ge=0)


# Calculation statistics
class CalculationStatistics(BaseModel):
    """Statistics for calculations."""
    total_calculations: int = Field(..., ge=0)
    completed_calculations: int = Field(..., ge=0)
    failed_calculations: int = Field(..., ge=0)
    pending_calculations: int = Field(..., ge=0)
    calculations_needing_review: int = Field(..., ge=0)
    calculations_by_type: Dict[str, int] = Field(default_factory=dict)
    success_rate: float = Field(..., ge=0, le=100)


# Calculation dashboard
class CalculationDashboard(BaseModel):
    """Dashboard data for calculations."""
    recent_calculations: List[CalculationSummary]
    failed_calculations: List[CalculationSummary]
    calculations_needing_review: List[CalculationSummary]
    statistics: CalculationStatistics


# Calculation result schema
class CalculationResult(BaseModel):
    """Schema for calculation results."""
    calculation_id: int
    status: str
    output_parameters: Dict[str, Any]
    error_message: Optional[str] = None
    completed_at: datetime


# Calculation review schema
class CalculationReview(BaseModel):
    """Schema for calculation review."""
    review_notes: Optional[str] = Field(None, max_length=2000)
    
    @validator('review_notes')
    def validate_review_notes(cls, v):
        """Validate review notes."""
        if v is not None and len(v.strip()) == 0:
            return None
        return v


# Calculation parameters schema for specific types
class PressureVesselParameters(BaseModel):
    """Parameters for pressure vessel calculations."""
    design_pressure: float = Field(..., gt=0, description="Design pressure (psi)")
    design_temperature: float = Field(..., description="Design temperature (°F)")
    internal_diameter: float = Field(..., gt=0, description="Internal diameter (in)")
    wall_thickness: float = Field(..., gt=0, description="Wall thickness (in)")
    material_designation: str = Field(..., description="Material designation")
    joint_efficiency: float = Field(default=1.0, ge=0.1, le=1.0, description="Joint efficiency")
    corrosion_allowance: float = Field(default=0.125, ge=0, description="Corrosion allowance (in)")
    
    @validator('design_pressure')
    def validate_design_pressure(cls, v):
        """Validate design pressure range."""
        if v > 3000:  # Typical pressure vessel limit
            raise ValueError("Design pressure exceeds typical pressure vessel limits")
        return v
    
    @validator('design_temperature')
    def validate_design_temperature(cls, v):
        """Validate design temperature range."""
        if v < -50 or v > 1000:  # Typical temperature range
            raise ValueError("Design temperature outside typical range (-50°F to 1000°F)")
        return v


class StressAnalysisParameters(BaseModel):
    """Parameters for stress analysis calculations."""
    applied_loads: Dict[str, float] = Field(..., description="Applied loads")
    boundary_conditions: Dict[str, Any] = Field(..., description="Boundary conditions")
    material_properties: Dict[str, float] = Field(..., description="Material properties")
    geometry: Dict[str, float] = Field(..., description="Geometry parameters")
    
    @validator('applied_loads')
    def validate_applied_loads(cls, v):
        """Validate applied loads."""
        required_loads = ['pressure', 'moment', 'axial_force']
        for load in required_loads:
            if load not in v:
                raise ValueError(f"Missing required load: {load}")
        return v


# Calculation template schema
class CalculationTemplate(BaseModel):
    """Template for common calculation types."""
    name: str = Field(..., min_length=1, max_length=200)
    calculation_type: str
    description: Optional[str] = Field(None, max_length=1000)
    default_parameters: Dict[str, Any] = Field(default_factory=dict)
    parameter_schema: Dict[str, Any] = Field(default_factory=dict)
    
    class Config:
        from_attributes = True
