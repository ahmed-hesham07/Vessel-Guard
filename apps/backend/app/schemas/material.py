"""
Pydantic schemas for Material model.

Defines request/response models for material API endpoints
with engineering property validation.
"""

from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel, validator, Field


class MaterialBase(BaseModel):
    """Base material schema with common fields."""
    
    name: str = Field(..., min_length=2, max_length=200, description="Material name")
    specification: str = Field(..., max_length=100, description="Material specification (e.g., SA-516)")
    grade: str = Field(..., max_length=50, description="Material grade (e.g., Grade 70)")
    description: Optional[str] = Field(None, max_length=1000, description="Material description")

    @validator('name')
    def validate_name(cls, v):
        """Validate material name."""
        if not v.strip():
            raise ValueError('Material name cannot be empty')
        return v.strip()

    @validator('specification')
    def validate_specification(cls, v):
        """Validate material specification."""
        if not v.strip():
            raise ValueError('Material specification cannot be empty')
        return v.strip().upper()

    @validator('grade')
    def validate_grade(cls, v):
        """Validate material grade."""
        if not v.strip():
            raise ValueError('Material grade cannot be empty')
        return v.strip()


class MaterialCreate(MaterialBase):
    """Schema for creating material."""
    
    # Mechanical properties
    yield_strength: Optional[float] = Field(None, gt=0, description="Yield strength (psi)")
    tensile_strength: Optional[float] = Field(None, gt=0, description="Tensile strength (psi)")
    elongation: Optional[float] = Field(None, ge=0, le=100, description="Elongation percentage")
    
    # Thermal properties
    thermal_expansion: Optional[float] = Field(None, ge=0, description="Thermal expansion coefficient")
    thermal_conductivity: Optional[float] = Field(None, ge=0, description="Thermal conductivity")
    
    # Temperature limits
    min_temp: Optional[float] = Field(None, description="Minimum temperature (°F)")
    max_temp: Optional[float] = Field(None, description="Maximum temperature (°F)")
    
    # Material properties
    density: Optional[float] = Field(None, gt=0, description="Density (lb/in³)")
    modulus_of_elasticity: Optional[float] = Field(None, gt=0, description="Modulus of elasticity (psi)")
    poisson_ratio: Optional[float] = Field(None, ge=0, le=0.5, description="Poisson's ratio")
    
    # Compliance flags
    is_asme_approved: bool = Field(default=False, description="ASME approved material")
    is_weldable: bool = Field(default=True, description="Weldable material")
    is_public: bool = Field(default=False, description="Public/standard material")

    @validator('tensile_strength')
    def validate_tensile_strength(cls, v, values):
        """Validate tensile strength is greater than yield strength."""
        if v is not None and 'yield_strength' in values and values['yield_strength']:
            if v <= values['yield_strength']:
                raise ValueError('Tensile strength must be greater than yield strength')
        return v

    @validator('max_temp')
    def validate_max_temp(cls, v, values):
        """Validate maximum temperature is greater than minimum temperature."""
        if v is not None and 'min_temp' in values and values['min_temp']:
            if v <= values['min_temp']:
                raise ValueError('Maximum temperature must be greater than minimum temperature')
        return v

    @validator('elongation')
    def validate_elongation(cls, v):
        """Validate elongation percentage."""
        if v is not None and (v < 0 or v > 100):
            raise ValueError('Elongation must be between 0 and 100 percent')
        return v

    @validator('poisson_ratio')
    def validate_poisson_ratio(cls, v):
        """Validate Poisson's ratio."""
        if v is not None and (v < 0 or v > 0.5):
            raise ValueError('Poisson\'s ratio must be between 0 and 0.5')
        return v


class MaterialUpdate(BaseModel):
    """Schema for updating material."""
    
    name: Optional[str] = Field(None, min_length=2, max_length=200)
    specification: Optional[str] = Field(None, max_length=100)
    grade: Optional[str] = Field(None, max_length=50)
    description: Optional[str] = Field(None, max_length=1000)
    
    # Mechanical properties
    yield_strength: Optional[float] = Field(None, gt=0)
    tensile_strength: Optional[float] = Field(None, gt=0)
    elongation: Optional[float] = Field(None, ge=0, le=100)
    
    # Thermal properties
    thermal_expansion: Optional[float] = Field(None, ge=0)
    thermal_conductivity: Optional[float] = Field(None, ge=0)
    
    # Temperature limits
    min_temp: Optional[float] = None
    max_temp: Optional[float] = None
    
    # Material properties
    density: Optional[float] = Field(None, gt=0)
    modulus_of_elasticity: Optional[float] = Field(None, gt=0)
    poisson_ratio: Optional[float] = Field(None, ge=0, le=0.5)
    
    # Compliance flags
    is_asme_approved: Optional[bool] = None
    is_weldable: Optional[bool] = None
    is_public: Optional[bool] = None
    is_active: Optional[bool] = None

    # Validators for optional fields
    @validator('name')
    def validate_name(cls, v):
        """Validate material name."""
        if v is not None:
            if not v.strip():
                raise ValueError('Material name cannot be empty')
            return v.strip()
        return v

    @validator('specification')
    def validate_specification(cls, v):
        """Validate material specification."""
        if v is not None:
            allowed_specs = ["ASTM", "ASME", "EN", "BS", "JIS", "DIN", "Other"]
            if not any(spec in v.upper() for spec in allowed_specs):
                raise ValueError(f'Specification must include one of: {", ".join(allowed_specs)}')
            return v.strip()
        return v

    @validator('grade')
    def validate_grade(cls, v):
        """Validate material grade."""
        if v is not None:
            if not v.strip():
                raise ValueError('Material grade cannot be empty')
            return v.strip()
        return v

    @validator('elongation')
    def validate_elongation(cls, v):
        """Validate elongation percentage."""
        if v is not None:
            if v < 0 or v > 100:
                raise ValueError('Elongation must be between 0 and 100 percent')
        return v

    @validator('poisson_ratio')
    def validate_poisson_ratio(cls, v):
        """Validate Poisson's ratio."""
        if v is not None:
            if v < 0 or v > 0.5:
                raise ValueError("Poisson's ratio must be between 0 and 0.5")
        return v


class MaterialInDBBase(MaterialBase):
    """Base schema for material in database."""
    
    id: int
    organization_id: Optional[int]
    created_by_id: Optional[int]
    updated_by_id: Optional[int]
    
    # Mechanical properties
    yield_strength: Optional[float]
    tensile_strength: Optional[float]
    elongation: Optional[float]
    
    # Thermal properties
    thermal_expansion: Optional[float]
    thermal_conductivity: Optional[float]
    
    # Temperature limits
    min_temp: Optional[float]
    max_temp: Optional[float]
    
    # Material properties
    density: Optional[float]
    modulus_of_elasticity: Optional[float]
    poisson_ratio: Optional[float]
    
    # Compliance flags
    is_asme_approved: bool
    is_weldable: bool
    is_public: bool
    is_active: bool
    
    # Timestamps
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


class Material(MaterialInDBBase):
    """Schema for material response."""
    pass


class MaterialWithUsage(Material):
    """Schema for material with usage statistics."""
    
    vessel_count: int = Field(..., description="Number of vessels using this material")
    calculation_count: int = Field(..., description="Number of calculations using this material")
    last_used: Optional[datetime] = Field(None, description="Last time material was used")


class MaterialSummary(BaseModel):
    """Schema for material summary (minimal info)."""
    
    id: int
    name: str
    specification: str
    grade: str
    is_asme_approved: bool
    is_weldable: bool
    is_public: bool

    class Config:
        from_attributes = True


class MaterialList(BaseModel):
    """Schema for paginated material list."""
    
    items: List[Material]
    total: int
    page: int
    per_page: int
    pages: int


class MaterialStatistics(BaseModel):
    """Schema for material statistics."""
    
    total_materials: int
    asme_approved: int
    weldable: int
    asme_approval_percentage: float
    weldable_percentage: float


class MaterialProperty(BaseModel):
    """Schema for material property response."""
    
    yield_strength: Optional[float] = Field(None, description="Yield strength")
    tensile_strength: Optional[float] = Field(None, description="Tensile strength")
    elongation: Optional[float] = Field(None, description="Elongation percentage")
    elastic_modulus: Optional[float] = Field(None, description="Elastic modulus")
    poisson_ratio: Optional[float] = Field(None, description="Poisson's ratio")
    thermal_expansion: Optional[float] = Field(None, description="Thermal expansion coefficient")
    thermal_conductivity: Optional[float] = Field(None, description="Thermal conductivity")
    density: Optional[float] = Field(None, description="Density")
    max_temperature: Optional[float] = Field(None, description="Maximum operating temperature")
    min_temperature: Optional[float] = Field(None, description="Minimum operating temperature")
    is_asme_compliant: Optional[bool] = Field(None, description="ASME compliance status")


class MaterialPropertyRange(BaseModel):
    """Schema for material property search criteria."""
    
    min_yield_strength: Optional[float] = Field(None, gt=0)
    max_yield_strength: Optional[float] = Field(None, gt=0)
    min_tensile_strength: Optional[float] = Field(None, gt=0)
    max_tensile_strength: Optional[float] = Field(None, gt=0)
    min_temperature: Optional[float] = None
    max_temperature: Optional[float] = None
    min_elongation: Optional[float] = Field(None, ge=0, le=100)
    max_elongation: Optional[float] = Field(None, ge=0, le=100)
    is_asme_approved: Optional[bool] = None
    is_weldable: Optional[bool] = None

    @validator('max_yield_strength')
    def validate_max_yield_strength(cls, v, values):
        """Validate max yield strength is greater than min."""
        if v is not None and 'min_yield_strength' in values and values['min_yield_strength']:
            if v <= values['min_yield_strength']:
                raise ValueError('Maximum yield strength must be greater than minimum')
        return v

    @validator('max_tensile_strength')
    def validate_max_tensile_strength(cls, v, values):
        """Validate max tensile strength is greater than min."""
        if v is not None and 'min_tensile_strength' in values and values['min_tensile_strength']:
            if v <= values['min_tensile_strength']:
                raise ValueError('Maximum tensile strength must be greater than minimum')
        return v

    @validator('max_temperature')
    def validate_max_temperature(cls, v, values):
        """Validate max temperature is greater than min."""
        if v is not None and 'min_temperature' in values and values['min_temperature']:
            if v <= values['min_temperature']:
                raise ValueError('Maximum temperature must be greater than minimum')
        return v


class MaterialComparison(BaseModel):
    """Schema for comparing materials."""
    
    materials: List[MaterialSummary]
    properties: List[str]
    comparison_matrix: dict


class StandardMaterial(BaseModel):
    """Schema for standard ASME materials."""
    
    name: str
    specification: str
    grade: str
    description: str
    yield_strength: float
    tensile_strength: float
    min_temp: Optional[float]
    max_temp: Optional[float]
    typical_applications: List[str]


class MaterialDashboard(BaseModel):
    """Schema for material dashboard response."""
    
    recent_materials: List[MaterialSummary] = Field(default_factory=list)
    most_used_materials: List[MaterialSummary] = Field(default_factory=list)
    asme_compliant_materials: List[MaterialSummary] = Field(default_factory=list)
    statistics: MaterialStatistics
