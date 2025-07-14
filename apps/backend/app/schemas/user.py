"""
User schemas for request/response models.

Defines Pydantic models for user-related endpoints
including user profiles and management.
"""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, EmailStr, Field, validator

from app.db.models.user import UserRole


class UserBase(BaseModel):
    """Base user model with common fields."""
    email: EmailStr
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    phone: Optional[str] = Field(None, max_length=20)
    job_title: Optional[str] = Field(None, max_length=100)
    department: Optional[str] = Field(None, max_length=100)
    timezone: str = Field(default="UTC", max_length=50)
    language: str = Field(default="en", max_length=10)


class UserCreate(UserBase):
    """User creation model."""
    password: str = Field(..., min_length=8)
    role: UserRole = Field(default=UserRole.VIEWER)
    organization_id: Optional[int] = None

    @validator('password')
    def validate_password(cls, v):
        """Validate password complexity."""
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        return v


class UserUpdate(BaseModel):
    """User update model."""
    first_name: Optional[str] = Field(None, min_length=1, max_length=100)
    last_name: Optional[str] = Field(None, min_length=1, max_length=100)
    phone: Optional[str] = Field(None, max_length=20)
    job_title: Optional[str] = Field(None, max_length=100)
    department: Optional[str] = Field(None, max_length=100)
    timezone: Optional[str] = Field(None, max_length=50)
    language: Optional[str] = Field(None, max_length=10)
    role: Optional[UserRole] = None
    is_active: Optional[bool] = None


class UserResponse(BaseModel):
    """User response model."""
    id: int
    email: EmailStr
    first_name: str
    last_name: str
    phone: Optional[str]
    job_title: Optional[str]
    department: Optional[str]
    role: UserRole
    is_active: bool
    is_verified: bool
    is_superuser: bool
    organization_id: int
    last_login: Optional[datetime]
    timezone: str
    language: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

    @property
    def full_name(self) -> str:
        """Get user's full name."""
        return f"{self.first_name} {self.last_name}"


class UserSummary(BaseModel):
    """User summary model for lists."""
    id: int
    email: EmailStr
    first_name: str
    last_name: str
    role: UserRole
    is_active: bool
    organization_id: int
    created_at: datetime

    class Config:
        from_attributes = True

    @property
    def full_name(self) -> str:
        """Get user's full name."""
        return f"{self.first_name} {self.last_name}"


# Alias for consistency with API endpoints
User = UserResponse


class UserProfile(UserResponse):
    """Schema for user profile with additional info."""
    
    login_count: int = Field(0, description="Number of times user has logged in")
    failed_login_attempts: int = Field(0, description="Number of failed login attempts")


class UserProfileUpdate(BaseModel):
    """User profile update model."""
    first_name: Optional[str] = Field(None, min_length=1, max_length=100)
    last_name: Optional[str] = Field(None, min_length=1, max_length=100)
    phone: Optional[str] = Field(None, max_length=20)
    job_title: Optional[str] = Field(None, max_length=100)
    department: Optional[str] = Field(None, max_length=100)
    timezone: Optional[str] = Field(None, max_length=50)


class UserList(BaseModel):
    """Schema for paginated user list."""
    
    items: List[User]
    total: int
    page: int
    per_page: int
    pages: int


class PasswordChange(BaseModel):
    """Schema for password change."""
    
    current_password: str = Field(..., min_length=1, description="Current password")
    new_password: str = Field(..., min_length=8, description="New password")
    confirm_password: str = Field(..., min_length=8, description="Confirm new password")

    @validator('confirm_password')
    def passwords_match(cls, v, values):
        """Validate that passwords match."""
        if 'new_password' in values and v != values['new_password']:
            raise ValueError('Passwords do not match')
        return v


class PasswordReset(BaseModel):
    """Schema for password reset request."""
    
    email: str = Field(..., description="User email address")

    @validator('email')
    def validate_email(cls, v):
        """Validate email format."""
        import re
        if not re.match(r'^[^@]+@[^@]+\.[^@]+$', v):
            raise ValueError('Invalid email format')
        return v.lower()
