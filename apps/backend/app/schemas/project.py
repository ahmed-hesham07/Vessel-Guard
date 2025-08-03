"""
Pydantic schemas for Project model.

Defines request/response models for project API endpoints
with validation and serialization.
"""

from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel, validator, Field


class ProjectBase(BaseModel):
    """Base project schema with common fields."""
    
    name: str = Field(..., min_length=2, max_length=200, description="Project name")
    description: Optional[str] = Field(None, max_length=1000, description="Project description")
    project_number: Optional[str] = Field(None, max_length=50, description="Project number/code")
    client_name: Optional[str] = Field(None, max_length=200, description="Client name")
    location: Optional[str] = Field(None, max_length=300, description="Project location")
    
    @validator('name')
    def validate_name(cls, v):
        """Validate project name."""
        if not v.strip():
            raise ValueError('Project name cannot be empty')
        return v.strip()


class ProjectCreate(ProjectBase):
    """Schema for creating project."""
    
    status: str = Field(default="planning", description="Initial project status")
    start_date: Optional[datetime] = Field(None, description="Project start date")
    end_date: Optional[datetime] = Field(None, description="Project end date")
    budget: Optional[float] = Field(None, ge=0, description="Project budget")

    @validator('status')
    def validate_status(cls, v):
        """Validate project status."""
        allowed_statuses = ["planning", "in_progress", "review", "completed", "cancelled", "on_hold"]
        if v not in allowed_statuses:
            raise ValueError(f'Project status must be one of: {", ".join(allowed_statuses)}')
        return v

    @validator('end_date')
    def validate_end_date(cls, v, values):
        """Validate end date is after start date."""
        if v and 'start_date' in values and values['start_date'] and v <= values['start_date']:
            raise ValueError('End date must be after start date')
        return v


class ProjectUpdate(BaseModel):
    """Schema for updating project."""
    
    name: Optional[str] = Field(None, min_length=2, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    project_number: Optional[str] = Field(None, max_length=50)
    client_name: Optional[str] = Field(None, max_length=200)
    location: Optional[str] = Field(None, max_length=300)
    status: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    actual_end_date: Optional[datetime] = None
    budget: Optional[float] = Field(None, ge=0)
    is_active: Optional[bool] = None

    @validator('name')
    def validate_name(cls, v):
        """Validate project name."""
        if v is not None and not v.strip():
            raise ValueError('Project name cannot be empty')
        return v.strip() if v else v

    @validator('status')
    def validate_status(cls, v):
        """Validate project status."""
        if v is not None:
            allowed_statuses = ["planning", "in_progress", "review", "completed", "cancelled", "on_hold"]
            if v not in allowed_statuses:
                raise ValueError(f'Project status must be one of: {", ".join(allowed_statuses)}')
        return v


class ProjectStatusUpdate(BaseModel):
    """Schema for updating project status only."""
    
    status: str = Field(..., description="New project status")

    @validator('status')
    def validate_status(cls, v):
        """Validate project status."""
        allowed_statuses = ["planning", "in_progress", "review", "completed", "cancelled", "on_hold"]
        if v not in allowed_statuses:
            raise ValueError(f'Project status must be one of: {", ".join(allowed_statuses)}')
        return v


class ProjectInDBBase(ProjectBase):
    """Base schema for project in database."""
    
    id: int
    organization_id: int
    owner_id: int  # Maps to created_by_id in frontend
    status: str
    start_date: Optional[datetime]
    target_completion_date: Optional[datetime]  # Maps to end_date in frontend
    actual_completion_date: Optional[datetime]  # Maps to actual_end_date in frontend
    created_at: datetime
    updated_at: Optional[datetime]
    
    # Optional fields that exist in the model
    client_contact: Optional[str] = None
    client_email: Optional[str] = None
    client_phone: Optional[str] = None
    priority: Optional[str] = None
    engineering_standards: Optional[dict] = None
    design_codes: Optional[dict] = None
    operating_environment: Optional[str] = None
    default_units: Optional[str] = None
    pressure_units: Optional[str] = None
    temperature_units: Optional[str] = None
    tags: Optional[dict] = None
    category: Optional[str] = None
    requires_certification: Optional[bool] = None
    certification_body: Optional[str] = None
    certification_requirements: Optional[str] = None

    class Config:
        from_attributes = True


class Project(ProjectInDBBase):
    """Schema for project response."""
    pass


class ProjectWithStats(Project):
    """Schema for project with statistics."""
    
    vessel_count: int = Field(..., description="Number of vessels in project")
    calculation_count: int = Field(..., description="Number of calculations in project")
    inspection_count: int = Field(..., description="Number of inspections in project")
    report_count: int = Field(..., description="Number of reports in project")
    progress_percentage: float = Field(..., description="Project completion percentage")
    days_remaining: Optional[int] = Field(None, description="Days until project due date")
    is_overdue: bool = Field(..., description="Whether project is overdue")


class ProjectSummary(BaseModel):
    """Schema for project summary (minimal info)."""
    
    id: int
    name: str
    project_number: Optional[str]
    status: str
    client_name: Optional[str]
    target_completion_date: Optional[datetime]  # Maps to end_date in frontend

    class Config:
        from_attributes = True
        
    @property
    def is_active(self) -> bool:
        """Check if project is currently active."""
        return self.status in ["active"]


class ProjectList(BaseModel):
    """Schema for paginated project list."""
    
    items: List[Project]
    total: int
    page: int
    per_page: int
    pages: int


class ProjectStatistics(BaseModel):
    """Schema for project statistics."""
    
    total_projects: int
    active_projects: int
    status_breakdown: dict
    overdue_projects: int
    due_soon_projects: int


class ProjectTimeline(BaseModel):
    """Schema for project timeline information."""
    
    project_id: int
    start_date: Optional[datetime]
    target_completion_date: Optional[datetime]  # Maps to end_date in frontend
    actual_completion_date: Optional[datetime]  # Maps to actual_end_date in frontend
    duration_days: Optional[int]
    remaining_days: Optional[int]
    progress_percentage: float
    is_overdue: bool
    milestone_count: int
    completed_milestones: int

    class Config:
        from_attributes = True


class ProjectDashboard(BaseModel):
    """Schema for project dashboard data."""
    
    recent_projects: List[ProjectSummary]
    overdue_projects: List[ProjectSummary]
    due_soon_projects: List[ProjectSummary]
    statistics: ProjectStatistics
    timeline_overview: List[ProjectTimeline]
