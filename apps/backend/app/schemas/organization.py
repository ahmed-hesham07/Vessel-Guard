"""
Pydantic schemas for Organization model.

Defines request/response models for organization API endpoints
with validation and serialization.
"""

from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel, validator, Field


class OrganizationBase(BaseModel):
    """Base organization schema with common fields."""
    
    name: str = Field(..., min_length=2, max_length=100, description="Organization name")
    description: Optional[str] = Field(None, max_length=500, description="Organization description")
    subdomain: Optional[str] = Field(None, min_length=3, max_length=50, description="Unique subdomain")
    website: Optional[str] = Field(None, max_length=200, description="Organization website")
    phone: Optional[str] = Field(None, max_length=20, description="Contact phone number")
    address: Optional[str] = Field(None, max_length=500, description="Organization address")

    @validator('subdomain')
    def validate_subdomain(cls, v):
        """Validate subdomain format."""
        if v is not None:
            # Only allow alphanumeric and hyphens, start with letter
            if not v.replace('-', '').isalnum() or not v[0].isalpha():
                raise ValueError('Subdomain must contain only letters, numbers, and hyphens, and start with a letter')
            if v.startswith('-') or v.endswith('-'):
                raise ValueError('Subdomain cannot start or end with hyphen')
        return v

    @validator('name')
    def validate_name(cls, v):
        """Validate organization name."""
        if not v.strip():
            raise ValueError('Organization name cannot be empty')
        return v.strip()


class OrganizationCreate(OrganizationBase):
    """Schema for creating organization."""
    
    subscription_tier: str = Field(default="free", description="Initial subscription tier")
    max_members: Optional[int] = Field(default=5, ge=1, description="Maximum members allowed")
    max_projects: Optional[int] = Field(default=3, ge=1, description="Maximum projects allowed")
    max_calculations_per_month: Optional[int] = Field(default=100, ge=1, description="Maximum calculations per month")

    @validator('subscription_tier')
    def validate_subscription_tier(cls, v):
        """Validate subscription tier."""
        allowed_tiers = ["free", "basic", "premium", "enterprise"]
        if v not in allowed_tiers:
            raise ValueError(f'Subscription tier must be one of: {", ".join(allowed_tiers)}')
        return v


class OrganizationUpdate(BaseModel):
    """Schema for updating organization."""
    
    name: Optional[str] = Field(None, min_length=2, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    subdomain: Optional[str] = Field(None, min_length=3, max_length=50)
    website: Optional[str] = Field(None, max_length=200)
    phone: Optional[str] = Field(None, max_length=20)
    address: Optional[str] = Field(None, max_length=500)
    is_active: Optional[bool] = None

    @validator('subdomain')
    def validate_subdomain(cls, v):
        """Validate subdomain format."""
        if v is not None:
            if not v.replace('-', '').isalnum() or not v[0].isalpha():
                raise ValueError('Subdomain must contain only letters, numbers, and hyphens, and start with a letter')
            if v.startswith('-') or v.endswith('-'):
                raise ValueError('Subdomain cannot start or end with hyphen')
        return v

    @validator('name')
    def validate_name(cls, v):
        """Validate organization name."""
        if v is not None and not v.strip():
            raise ValueError('Organization name cannot be empty')
        return v.strip() if v else v


class OrganizationSubscriptionUpdate(BaseModel):
    """Schema for updating organization subscription."""
    
    subscription_tier: str = Field(..., description="Subscription tier")
    subscription_expires_at: Optional[datetime] = Field(None, description="Subscription expiration date")
    max_members: Optional[int] = Field(None, ge=1, description="Maximum members allowed")
    max_projects: Optional[int] = Field(None, ge=1, description="Maximum projects allowed")
    max_calculations_per_month: Optional[int] = Field(None, ge=1, description="Maximum calculations per month")

    @validator('subscription_tier')
    def validate_subscription_tier(cls, v):
        """Validate subscription tier."""
        allowed_tiers = ["free", "basic", "premium", "enterprise"]
        if v not in allowed_tiers:
            raise ValueError(f'Subscription tier must be one of: {", ".join(allowed_tiers)}')
        return v

    @validator('subscription_expires_at')
    def validate_expiration_date(cls, v):
        """Validate subscription expiration date."""
        if v is not None and v <= datetime.utcnow():
            raise ValueError('Subscription expiration date must be in the future')
        return v


class OrganizationInDBBase(OrganizationBase):
    """Base schema for organization in database."""
    
    id: int
    subscription_tier: str
    subscription_expires_at: Optional[datetime]
    max_members: Optional[int]
    max_projects: Optional[int]
    max_calculations_per_month: Optional[int]
    calculations_this_month: Optional[int]
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


class Organization(OrganizationInDBBase):
    """Schema for organization response."""
    pass


class OrganizationWithStats(Organization):
    """Schema for organization with usage statistics."""
    
    member_count: int = Field(..., description="Current number of members")
    project_count: int = Field(..., description="Current number of projects")
    calculation_usage_percentage: float = Field(..., description="Percentage of monthly calculations used")


class OrganizationSummary(BaseModel):
    """Schema for organization summary (minimal info)."""
    
    id: int
    name: str
    subdomain: Optional[str]
    subscription_tier: str
    is_active: bool

    class Config:
        from_attributes = True


class OrganizationList(BaseModel):
    """Schema for paginated organization list."""
    
    items: List[Organization]
    total: int
    page: int
    per_page: int
    pages: int


class OrganizationUsageStats(BaseModel):
    """Schema for organization usage statistics."""
    
    organization_id: int
    member_count: int
    project_count: int
    calculations_this_month: int
    max_calculations_per_month: Optional[int]
    calculations_remaining: Optional[int]
    subscription_tier: str
    subscription_expires_at: Optional[datetime]
    days_until_expiration: Optional[int]

    class Config:
        from_attributes = True
