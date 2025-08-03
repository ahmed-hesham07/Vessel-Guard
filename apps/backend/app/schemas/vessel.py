"""
Pydantic schemas for Vessel model.

Defines request/response models for vessel API endpoints
with validation and engineering parameter constraints.
"""

from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel, validator, Field


class VesselBase(BaseModel):
    """Base vessel schema with common fields."""
    
    tag_number: str = Field(..., min_length=1, max_length=50, description="Unique vessel tag number")
    name: str = Field(..., min_length=2, max_length=200, description="Vessel name")
    description: Optional[str] = Field(None, max_length=1000, description="Vessel description")
    vessel_type: str = Field(..., description="Type of vessel")
    service_fluid: Optional[str] = Field(None, max_length=200, description="Vessel service fluid/purpose")
    location: Optional[str] = Field(None, max_length=200, description="Vessel location")

    @validator('tag_number')
    def validate_tag_number(cls, v):
        """Validate tag number format."""
        if not v.strip():
            raise ValueError('Tag number cannot be empty')
        # Remove spaces and convert to uppercase
        return v.strip().upper()

    @validator('name')
    def validate_name(cls, v):
        """Validate vessel name."""
        if not v.strip():
            raise ValueError('Vessel name cannot be empty')
        return v.strip()

    @validator('vessel_type')
    def validate_vessel_type(cls, v):
        """Validate vessel type."""
        allowed_types = [
            "pressure_vessel", "storage_tank", "heat_exchanger", 
            "reactor", "column", "separator", "filter", "piping", "air_cooling", "other"
        ]
        if v not in allowed_types:
            raise ValueError(f'Vessel type must be one of: {", ".join(allowed_types)}')
        return v


class VesselCreate(VesselBase):
    """Schema for creating vessel."""
    
    # Design parameters
    design_code: str = Field(..., description="Design code (e.g., ASME VIII)")
    design_pressure: float = Field(..., gt=0, description="Design pressure")
    design_temperature: float = Field(..., description="Design temperature")
    operating_pressure: Optional[float] = Field(None, ge=0, description="Operating pressure")
    operating_temperature: Optional[float] = Field(None, description="Operating temperature")
    
    # Geometric parameters
    inside_diameter: Optional[float] = Field(None, gt=0, description="Inside diameter")
    outside_diameter: Optional[float] = Field(None, gt=0, description="Outside diameter")
    wall_thickness: Optional[float] = Field(None, gt=0, description="Wall thickness")
    overall_length: Optional[float] = Field(None, gt=0, description="Overall length")
    head_type: Optional[str] = Field(None, description="Head type")
    
    # Material and corrosion
    material_id: Optional[int] = Field(None, description="Material ID")
    corrosion_allowance: Optional[float] = Field(None, ge=0, description="Corrosion allowance")
    joint_efficiency: Optional[float] = Field(None, ge=0, le=1, description="Joint efficiency")
    
    # Dates
    installation_date: Optional[datetime] = Field(None, description="Installation date")
    last_inspection_date: Optional[datetime] = Field(None, description="Last inspection date")
    next_inspection_date: Optional[datetime] = Field(None, description="Next inspection date")

    @validator('design_code')
    def validate_design_code(cls, v):
        """Validate design code."""
        allowed_codes = [
            "ASME VIII Div 1", "ASME VIII Div 2", "ASME I", 
            "API 650", "API 620", "PD 5500", "EN 13445", "Other"
        ]
        if v not in allowed_codes:
            raise ValueError(f'Design code must be one of: {", ".join(allowed_codes)}')
        return v

    @validator('operating_pressure')
    def validate_operating_pressure(cls, v, values):
        """Validate operating pressure is less than design pressure."""
        if v is not None and 'design_pressure' in values and v > values['design_pressure']:
            raise ValueError('Operating pressure cannot exceed design pressure')
        return v

    @validator('operating_temperature')
    def validate_operating_temperature(cls, v, values):
        """Validate operating temperature is within design temperature."""
        if v is not None and 'design_temperature' in values:
            # Allow some tolerance for operating temperature
            if abs(v) > abs(values['design_temperature']) + 50:
                raise ValueError('Operating temperature should be within design temperature range')
        return v

    @validator('outside_diameter')
    def validate_outside_diameter(cls, v, values):
        """Validate outside diameter is greater than inside diameter."""
        if v is not None and 'inside_diameter' in values and values['inside_diameter']:
            if v <= values['inside_diameter']:
                raise ValueError('Outside diameter must be greater than inside diameter')
        return v

    @validator('head_type')
    def validate_head_type(cls, v):
        """Validate head type."""
        if v is not None:
            allowed_types = [
                "ellipsoidal", "hemispherical", "torispherical", 
                "flat", "conical", "other"
            ]
            if v not in allowed_types:
                raise ValueError(f'Head type must be one of: {", ".join(allowed_types)}')
        return v

    @validator('next_inspection_date')
    def validate_next_inspection_date(cls, v, values):
        """Validate next inspection date is after last inspection date."""
        if (v is not None and 'last_inspection_date' in values and 
            values['last_inspection_date'] and v <= values['last_inspection_date']):
            raise ValueError('Next inspection date must be after last inspection date')
        return v


class VesselUpdate(BaseModel):
    """Schema for updating vessel."""
    
    tag_number: Optional[str] = Field(None, min_length=1, max_length=50)
    name: Optional[str] = Field(None, min_length=2, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    vessel_type: Optional[str] = None
    service_fluid: Optional[str] = Field(None, max_length=200)
    location: Optional[str] = Field(None, max_length=200)
    
    # Design parameters
    design_code: Optional[str] = None
    design_pressure: Optional[float] = Field(None, gt=0)
    design_temperature: Optional[float] = None
    operating_pressure: Optional[float] = Field(None, ge=0)
    operating_temperature: Optional[float] = None
    
    # Geometric parameters
    inside_diameter: Optional[float] = Field(None, gt=0)
    outside_diameter: Optional[float] = Field(None, gt=0)
    wall_thickness: Optional[float] = Field(None, gt=0)
    overall_length: Optional[float] = Field(None, gt=0)
    head_type: Optional[str] = None
    
    # Material and corrosion
    material_id: Optional[int] = None
    corrosion_allowance: Optional[float] = Field(None, ge=0)
    joint_efficiency: Optional[float] = Field(None, ge=0, le=1)
    
    # Dates
    installation_date: Optional[datetime] = None
    last_inspection_date: Optional[datetime] = None
    next_inspection_date: Optional[datetime] = None
    
    # Status
    is_active: Optional[bool] = None

    # Validators for optional fields
    @validator('tag_number')
    def validate_tag_number(cls, v):
        """Validate tag number format."""
        if v is not None:
            if not v.strip():
                raise ValueError('Tag number cannot be empty')
            return v.strip().upper()
        return v

    @validator('name')
    def validate_name(cls, v):
        """Validate vessel name."""
        if v is not None:
            if not v.strip():
                raise ValueError('Vessel name cannot be empty')
            return v.strip()
        return v

    @validator('vessel_type')
    def validate_vessel_type(cls, v):
        """Validate vessel type."""
        if v is not None:
            allowed_types = [
                "pressure_vessel", "storage_tank", "heat_exchanger", 
                "reactor", "column", "separator", "filter", "piping", "air_cooling", "other"
            ]
            if v not in allowed_types:
                raise ValueError(f'Vessel type must be one of: {", ".join(allowed_types)}')
        return v

    @validator('design_code')
    def validate_design_code(cls, v):
        """Validate design code."""
        if v is not None:
            allowed_codes = ["ASME VIII Div 1", "ASME VIII Div 2", "EN 13445", "BS 5500", "Other"]
            if v not in allowed_codes:
                raise ValueError(f'Design code must be one of: {", ".join(allowed_codes)}')
        return v

    @validator('head_type')
    def validate_head_type(cls, v):
        """Validate head type."""
        if v is not None:
            allowed_types = ["ellipsoidal", "hemispherical", "torispherical", "flat", "conical"]
            if v not in allowed_types:
                raise ValueError(f'Head type must be one of: {", ".join(allowed_types)}')
        return v


class VesselInspectionUpdate(BaseModel):
    """Schema for updating vessel inspection dates."""
    
    last_inspection_date: Optional[datetime] = Field(None, description="Last inspection date")
    next_inspection_date: datetime = Field(..., description="Next inspection date")

    @validator('next_inspection_date')
    def validate_next_inspection_date(cls, v, values):
        """Validate next inspection date is after last inspection date."""
        if (v is not None and 'last_inspection_date' in values and 
            values['last_inspection_date'] and v <= values['last_inspection_date']):
            raise ValueError('Next inspection date must be after last inspection date')
        if v <= datetime.utcnow():
            raise ValueError('Next inspection date must be in the future')
        return v


class VesselInDBBase(VesselBase):
    """Base schema for vessel in database."""
    
    id: int
    project_id: int
    organization_id: int
    created_by_id: int
    updated_by_id: Optional[int]
    
    # Design parameters
    design_code: str
    design_pressure: float
    design_temperature: float
    operating_pressure: Optional[float]
    operating_temperature: Optional[float]
    
    # Geometric parameters
    inside_diameter: Optional[float]
    outside_diameter: Optional[float]
    wall_thickness: Optional[float]
    overall_length: Optional[float]
    head_type: Optional[str]
    
    # Material and corrosion
    material_id: Optional[int]
    corrosion_allowance: Optional[float]
    joint_efficiency: Optional[float]
    
    # Dates
    installation_date: Optional[datetime]
    last_inspection_date: Optional[datetime]
    next_inspection_date: Optional[datetime]
    
    # Status
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


class Vessel(VesselInDBBase):
    """Schema for vessel response."""
    pass


class VesselWithStats(Vessel):
    """Schema for vessel with statistics."""
    
    calculation_count: int = Field(..., description="Number of calculations")
    inspection_count: int = Field(..., description="Number of inspections")
    days_until_inspection: Optional[int] = Field(None, description="Days until next inspection")
    is_overdue_inspection: bool = Field(..., description="Whether inspection is overdue")
    safety_factor: Optional[float] = Field(None, description="Safety factor")
    remaining_life: Optional[float] = Field(None, description="Estimated remaining life")


class VesselSummary(BaseModel):
    """Schema for vessel summary (minimal info)."""
    
    id: int
    tag_number: str
    name: str
    vessel_type: str
    service_fluid: Optional[str]
    next_inspection_date: Optional[datetime]
    is_active: bool

    class Config:
        from_attributes = True


class VesselList(BaseModel):
    """Schema for paginated vessel list."""
    
    items: List[Vessel]
    total: int
    page: int
    per_page: int
    pages: int


class VesselStatistics(BaseModel):
    """Schema for vessel statistics."""
    
    total_vessels: int
    type_breakdown: dict
    code_breakdown: dict
    overdue_inspections: int
    due_soon_inspections: int
    critical_vessels: int


class VesselInspectionSchedule(BaseModel):
    """Schema for vessel inspection schedule."""
    
    vessel_id: int
    tag_number: str
    name: str
    last_inspection_date: Optional[datetime]
    next_inspection_date: Optional[datetime]
    days_until_inspection: Optional[int]
    is_overdue: bool
    inspection_type: str
    priority: str

    class Config:
        from_attributes = True


class VesselDashboard(BaseModel):
    """Schema for vessel dashboard data."""
    
    critical_vessels: List[VesselSummary]
    overdue_inspections: List[VesselInspectionSchedule]
    due_soon_inspections: List[VesselInspectionSchedule]
    statistics: VesselStatistics
