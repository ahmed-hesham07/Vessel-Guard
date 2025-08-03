"""
Pydantic schemas for inspections.

Request/response models for vessel inspection tracking including
scheduling, results recording, and compliance management.
"""

from datetime import datetime, date
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field, validator


# Base inspection schema
class InspectionBase(BaseModel):
    """Base inspection schema with common fields."""
    inspection_type: str = Field(..., min_length=1, max_length=50, description="Type of inspection")
    inspection_date: date = Field(..., description="Date of inspection")
    inspector_name: str = Field(..., min_length=1, max_length=100, description="Inspector name")
    inspector_certification: Optional[str] = Field(None, max_length=100, description="Inspector certification")
    findings: Optional[str] = Field(None, max_length=2000, description="Inspection findings")
    recommendations: Optional[str] = Field(None, max_length=2000, description="Recommendations")
    result: str = Field(..., description="Inspection result")
    
    @validator('inspection_type')
    def validate_inspection_type(cls, v):
        """Validate inspection type."""
        allowed_types = [
            "visual", "ultrasonic", "radiographic", "magnetic_particle",
            "liquid_penetrant", "eddy_current", "pressure_test", 
            "leak_test", "thickness_measurement", "regulatory", "other"
        ]
        if v not in allowed_types:
            raise ValueError(f"Inspection type must be one of: {', '.join(allowed_types)}")
        return v
    
    @validator('result')
    def validate_result(cls, v):
        """Validate inspection result."""
        allowed_results = ["pass", "fail", "conditional", "not_applicable"]
        if v not in allowed_results:
            raise ValueError(f"Result must be one of: {', '.join(allowed_results)}")
        return v


# Create inspection schema
class InspectionCreate(InspectionBase):
    """Schema for creating a new inspection."""
    vessel_id: int = Field(..., gt=0, description="Vessel ID")
    next_inspection_date: Optional[date] = Field(None, description="Next inspection due date")
    inspection_interval_months: Optional[int] = Field(None, ge=1, le=120, description="Inspection interval in months")
    
    @validator('next_inspection_date')
    def validate_next_inspection_date(cls, v, values):
        """Validate next inspection date is after current inspection."""
        if v and 'inspection_date' in values and v <= values['inspection_date']:
            raise ValueError("Next inspection date must be after current inspection date")
        return v


# Update inspection schema
class InspectionUpdate(BaseModel):
    """Schema for updating inspection."""
    inspection_type: Optional[str] = Field(None, min_length=1, max_length=50)
    inspection_date: Optional[date] = Field(None)
    inspector_name: Optional[str] = Field(None, min_length=1, max_length=100)
    inspector_certification: Optional[str] = Field(None, max_length=100)
    findings: Optional[str] = Field(None, max_length=2000)
    recommendations: Optional[str] = Field(None, max_length=2000)
    result: Optional[str] = Field(None)
    status: Optional[str] = Field(None, description="Inspection status")
    next_inspection_date: Optional[date] = Field(None)
    inspection_interval_months: Optional[int] = Field(None, ge=1, le=120)
    
    @validator('inspection_type')
    def validate_inspection_type(cls, v):
        """Validate inspection type."""
        if v is not None:
            allowed_types = [
                "visual", "ultrasonic", "radiographic", "magnetic_particle",
                "liquid_penetrant", "eddy_current", "pressure_test", 
                "leak_test", "thickness_measurement", "regulatory", "other"
            ]
            if v not in allowed_types:
                raise ValueError(f"Inspection type must be one of: {', '.join(allowed_types)}")
        return v
    
    @validator('result')
    def validate_result(cls, v):
        """Validate inspection result."""
        if v is not None:
            allowed_results = ["pass", "fail", "conditional", "not_applicable"]
            if v not in allowed_results:
                raise ValueError(f"Result must be one of: {', '.join(allowed_results)}")
        return v
    
    @validator('status')
    def validate_status(cls, v):
        """Validate inspection status."""
        if v is not None:
            allowed_statuses = ["scheduled", "in_progress", "completed", "cancelled", "overdue"]
            if v not in allowed_statuses:
                raise ValueError(f"Status must be one of: {', '.join(allowed_statuses)}")
        return v


# Inspection response schema
class Inspection(InspectionBase):
    """Full inspection schema for responses."""
    id: int
    vessel_id: int
    next_inspection_date: Optional[date] = None
    inspection_interval_months: Optional[int] = None
    created_by_id: int
    updated_by_id: Optional[int] = None
    created_at: datetime
    updated_at: datetime
    is_active: bool

    class Config:
        from_attributes = True


# Inspection summary schema
class InspectionSummary(BaseModel):
    """Summary schema for inspection lists."""
    id: int
    inspection_type: str
    inspection_date: date
    inspector_name: str
    result: str
    vessel_id: int
    next_inspection_date: Optional[date] = None
    
    class Config:
        from_attributes = True


# Inspection with vessel info
class InspectionWithVessel(Inspection):
    """Inspection with vessel information."""
    vessel_tag_number: Optional[str] = None
    vessel_name: Optional[str] = None


# Inspection list schema
class InspectionList(BaseModel):
    """Schema for paginated inspection lists."""
    items: List[Inspection]
    total: int = Field(..., ge=0)
    page: int = Field(..., ge=1)
    per_page: int = Field(..., ge=1)
    pages: int = Field(..., ge=0)


# Inspection statistics
class InspectionStatistics(BaseModel):
    """Statistics for inspections."""
    total_inspections: int = Field(..., ge=0)
    passed_inspections: int = Field(..., ge=0)
    failed_inspections: int = Field(..., ge=0)
    overdue_inspections: int = Field(..., ge=0)
    due_soon_inspections: int = Field(..., ge=0)
    inspections_by_type: Dict[str, int] = Field(default_factory=dict)
    pass_rate: float = Field(..., ge=0, le=100)


# Inspection dashboard
class InspectionDashboard(BaseModel):
    """Dashboard data for inspections."""
    recent_inspections: List[InspectionSummary]
    overdue_inspections: List[InspectionSummary]
    due_soon_inspections: List[InspectionSummary]
    failed_inspections: List[InspectionSummary]
    statistics: InspectionStatistics


# Inspection schedule schema
class InspectionSchedule(BaseModel):
    """Schema for inspection scheduling."""
    vessel_id: int
    vessel_tag_number: str
    vessel_name: str
    last_inspection_date: Optional[date] = None
    next_inspection_date: Optional[date] = None
    days_until_inspection: Optional[int] = None
    is_overdue: bool = False
    inspection_type: str
    priority: str = Field(default="Medium")
    
    @validator('priority')
    def validate_priority(cls, v):
        """Validate priority level."""
        allowed_priorities = ["Low", "Medium", "High", "Critical"]
        if v not in allowed_priorities:
            raise ValueError(f"Priority must be one of: {', '.join(allowed_priorities)}")
        return v


# Inspection calendar event
class InspectionCalendarEvent(BaseModel):
    """Schema for calendar display of inspections."""
    id: int
    title: str
    date: date
    vessel_tag_number: str
    inspection_type: str
    is_overdue: bool
    priority: str
    
    class Config:
        from_attributes = True


# Inspection checklist item
class InspectionChecklistItem(BaseModel):
    """Individual checklist item for inspections."""
    item_id: str = Field(..., min_length=1, max_length=50)
    description: str = Field(..., min_length=1, max_length=500)
    is_required: bool = Field(default=True)
    is_completed: bool = Field(default=False)
    result: Optional[str] = Field(None)
    notes: Optional[str] = Field(None, max_length=1000)
    
    @validator('result')
    def validate_result(cls, v):
        """Validate checklist item result."""
        if v is not None:
            allowed_results = ["pass", "fail", "not_applicable", "needs_attention"]
            if v not in allowed_results:
                raise ValueError(f"Result must be one of: {', '.join(allowed_results)}")
        return v


# Inspection checklist
class InspectionChecklist(BaseModel):
    """Complete inspection checklist."""
    inspection_type: str
    checklist_items: List[InspectionChecklistItem] = Field(default_factory=list)
    completion_percentage: float = Field(default=0.0, ge=0, le=100)
    
    @validator('completion_percentage')
    def calculate_completion(cls, v, values):
        """Calculate completion percentage based on checklist items."""
        if 'checklist_items' in values:
            items = values['checklist_items']
            if items:
                completed = sum(1 for item in items if item.is_completed)
                return round((completed / len(items)) * 100, 2)
        return v


# Inspection report data
class InspectionReportData(BaseModel):
    """Data for generating inspection reports."""
    inspection: Inspection
    vessel_info: Dict[str, Any]
    checklist: Optional[InspectionChecklist] = None
    photos: List[str] = Field(default_factory=list)
    drawings: List[str] = Field(default_factory=list)
    previous_inspections: List[InspectionSummary] = Field(default_factory=list)


# Inspection finding
class InspectionFinding(BaseModel):
    """Individual finding from inspection."""
    finding_id: str = Field(..., min_length=1, max_length=50)
    severity: str = Field(..., description="Severity level")
    location: str = Field(..., min_length=1, max_length=200)
    description: str = Field(..., min_length=1, max_length=1000)
    recommendation: Optional[str] = Field(None, max_length=1000)
    corrective_action: Optional[str] = Field(None, max_length=1000)
    due_date: Optional[date] = Field(None)
    status: str = Field(default="open")
    
    @validator('severity')
    def validate_severity(cls, v):
        """Validate finding severity."""
        allowed_severities = ["low", "medium", "high", "critical"]
        if v not in allowed_severities:
            raise ValueError(f"Severity must be one of: {', '.join(allowed_severities)}")
        return v
    
    @validator('status')
    def validate_status(cls, v):
        """Validate finding status."""
        allowed_statuses = ["open", "in_progress", "resolved", "deferred"]
        if v not in allowed_statuses:
            raise ValueError(f"Status must be one of: {', '.join(allowed_statuses)}")
        return v


# Detailed inspection with findings
class DetailedInspection(Inspection):
    """Inspection with detailed findings and checklist."""
    checklist: Optional[InspectionChecklist] = None
    findings: List[InspectionFinding] = Field(default_factory=list)
    photos: List[str] = Field(default_factory=list)
    drawings: List[str] = Field(default_factory=list)
