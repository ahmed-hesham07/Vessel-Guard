"""
Pydantic schemas for reports.

Request/response models for report generation, storage, and retrieval
for vessels, calculations, and inspections.
"""

from datetime import datetime
from typing import Optional, Dict, Any, List, Union
from pydantic import BaseModel, Field, validator


# Base report schema
class ReportBase(BaseModel):
    """Base report schema with common fields."""
    name: str = Field(..., min_length=1, max_length=200, description="Report name")
    description: Optional[str] = Field(None, max_length=1000, description="Report description")
    report_type: str = Field(..., min_length=1, max_length=50, description="Type of report")
    format: str = Field(default="pdf", description="Report format")
    
    @validator('report_type')
    def validate_report_type(cls, v):
        """Validate report type."""
        allowed_types = [
            "vessel_datasheet", "calculation_report", "inspection_report",
            "compliance_report", "design_report", "stress_analysis",
            "material_certificate", "pressure_test", "project_summary", "other"
        ]
        if v not in allowed_types:
            raise ValueError(f"Report type must be one of: {', '.join(allowed_types)}")
        return v
    
    @validator('format')
    def validate_format(cls, v):
        """Validate report format."""
        allowed_formats = ["pdf", "docx", "xlsx", "html", "csv"]
        if v not in allowed_formats:
            raise ValueError(f"Format must be one of: {', '.join(allowed_formats)}")
        return v


# Create report schema
class ReportCreate(ReportBase):
    """Schema for creating a new report."""
    vessel_id: int = Field(..., gt=0, description="Vessel ID")
    calculation_id: Optional[int] = Field(None, gt=0, description="Calculation ID")
    inspection_id: Optional[int] = Field(None, gt=0, description="Inspection ID")
    template_id: Optional[int] = Field(None, gt=0, description="Report template ID")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Report parameters")
    
    @validator('parameters')
    def validate_parameters(cls, v):
        """Validate report parameters."""
        if not isinstance(v, dict):
            raise ValueError("Parameters must be a dictionary")
        return v


# Update report schema
class ReportUpdate(BaseModel):
    """Schema for updating report."""
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    parameters: Optional[Dict[str, Any]] = Field(None)
    status: Optional[str] = Field(None)
    error_message: Optional[str] = Field(None)
    
    @validator('status')
    def validate_status(cls, v):
        """Validate report status."""
        if v is not None:
            allowed_statuses = ["pending", "generating", "completed", "failed"]
            if v not in allowed_statuses:
                raise ValueError(f"Status must be one of: {', '.join(allowed_statuses)}")
        return v


# Report response schema
class Report(ReportBase):
    """Full report schema for responses."""
    id: int
    vessel_id: int
    calculation_id: Optional[int] = None
    inspection_id: Optional[int] = None
    template_id: Optional[int] = None
    parameters: Dict[str, Any] = Field(default_factory=dict)
    status: str = Field(default="pending")
    file_path: Optional[str] = None
    file_size: Optional[int] = None
    error_message: Optional[str] = None
    created_by_id: int
    generated_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    is_active: bool

    class Config:
        from_attributes = True


# Report summary schema
class ReportSummary(BaseModel):
    """Summary schema for report lists."""
    id: int
    name: str
    report_type: str
    format: str
    status: str
    vessel_id: int
    file_size: Optional[int] = None
    created_at: datetime
    generated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# Report with vessel info
class ReportWithVessel(Report):
    """Report with vessel information."""
    vessel_tag_number: Optional[str] = None
    vessel_name: Optional[str] = None


# Report list schema
class ReportList(BaseModel):
    """Schema for paginated report lists."""
    items: List[Report]
    total: int = Field(..., ge=0)
    page: int = Field(..., ge=1)
    per_page: int = Field(..., ge=1)
    pages: int = Field(..., ge=0)


# Report statistics
class ReportStatistics(BaseModel):
    """Statistics for reports."""
    total_reports: int = Field(..., ge=0)
    completed_reports: int = Field(..., ge=0)
    failed_reports: int = Field(..., ge=0)
    generating_reports: int = Field(..., ge=0)
    reports_by_type: Dict[str, int] = Field(default_factory=dict)
    reports_by_format: Dict[str, int] = Field(default_factory=dict)
    success_rate: float = Field(..., ge=0, le=100)
    total_file_size_mb: float = Field(..., ge=0)


# Report dashboard
class ReportDashboard(BaseModel):
    """Dashboard data for reports."""
    recent_reports: List[ReportSummary]
    pending_reports: List[ReportSummary]
    failed_reports: List[ReportSummary]
    downloadable_reports: List[ReportSummary]
    statistics: ReportStatistics


# Report template schema
class ReportTemplate(BaseModel):
    """Template for report generation."""
    id: int
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    report_type: str
    format: str
    template_path: str
    parameter_schema: Dict[str, Any] = Field(default_factory=dict)
    is_active: bool = True
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# Report template create schema
class ReportTemplateCreate(BaseModel):
    """Schema for creating report template."""
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    report_type: str
    format: str = Field(default="pdf")
    template_path: str = Field(..., min_length=1)
    parameter_schema: Dict[str, Any] = Field(default_factory=dict)


# Report generation request
class ReportGenerationRequest(BaseModel):
    """Request schema for report generation."""
    vessel_id: int = Field(..., gt=0)
    report_type: str
    format: str = Field(default="pdf")
    template_id: Optional[int] = Field(None, gt=0)
    parameters: Dict[str, Any] = Field(default_factory=dict)
    include_calculations: bool = Field(default=False)
    include_inspections: bool = Field(default=False)
    include_photos: bool = Field(default=False)
    include_drawings: bool = Field(default=False)


# Report download info
class ReportDownloadInfo(BaseModel):
    """Information for downloading reports."""
    report_id: int
    filename: str
    content_type: str
    file_size: int
    download_url: str
    expires_at: datetime


# Report data for generation
class VesselDatasheetData(BaseModel):
    """Data for vessel datasheet report."""
    vessel: Dict[str, Any]
    project: Dict[str, Any]
    material: Optional[Dict[str, Any]] = None
    calculations: List[Dict[str, Any]] = Field(default_factory=list)
    inspections: List[Dict[str, Any]] = Field(default_factory=list)
    organization: Dict[str, Any]


class CalculationReportData(BaseModel):
    """Data for calculation report."""
    calculation: Dict[str, Any]
    vessel: Dict[str, Any]
    material: Optional[Dict[str, Any]] = None
    project: Dict[str, Any]
    organization: Dict[str, Any]
    code_compliance: Dict[str, Any] = Field(default_factory=dict)


class InspectionReportData(BaseModel):
    """Data for inspection report."""
    inspection: Dict[str, Any]
    vessel: Dict[str, Any]
    project: Dict[str, Any]
    organization: Dict[str, Any]
    previous_inspections: List[Dict[str, Any]] = Field(default_factory=list)
    findings: List[Dict[str, Any]] = Field(default_factory=list)
    photos: List[str] = Field(default_factory=list)


class ComplianceReportData(BaseModel):
    """Data for compliance report."""
    vessels: List[Dict[str, Any]]
    inspections: List[Dict[str, Any]]
    calculations: List[Dict[str, Any]]
    organization: Dict[str, Any]
    compliance_summary: Dict[str, Any]
    period: Dict[str, Any]


# Report batch generation
class ReportBatchRequest(BaseModel):
    """Request for generating multiple reports."""
    vessel_ids: List[int] = Field(..., min_items=1, max_items=50)
    report_type: str
    format: str = Field(default="pdf")
    template_id: Optional[int] = Field(None, gt=0)
    parameters: Dict[str, Any] = Field(default_factory=dict)
    combine_reports: bool = Field(default=False)
    
    @validator('vessel_ids')
    def validate_vessel_ids(cls, v):
        """Validate vessel IDs list."""
        if len(set(v)) != len(v):
            raise ValueError("Vessel IDs must be unique")
        return v


# Report export options
class ReportExportOptions(BaseModel):
    """Options for report export."""
    include_metadata: bool = Field(default=True)
    include_attachments: bool = Field(default=True)
    compression_level: int = Field(default=5, ge=1, le=9)
    password_protect: bool = Field(default=False)
    watermark: Optional[str] = Field(None, max_length=100)
    
    @validator('watermark')
    def validate_watermark(cls, v):
        """Validate watermark text."""
        if v is not None and len(v.strip()) == 0:
            return None
        return v


# Report archive schema
class ReportArchive(BaseModel):
    """Schema for archived reports."""
    archive_id: str
    name: str
    description: Optional[str] = None
    report_ids: List[int]
    archive_path: str
    file_size: int
    created_by_id: int
    created_at: datetime
    expires_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# Report sharing schema
class ReportShare(BaseModel):
    """Schema for sharing reports."""
    report_id: int
    shared_with_email: str = Field(..., pattern=r'^[^@]+@[^@]+\.[^@]+$')
    access_level: str = Field(default="view")
    expires_at: Optional[datetime] = None
    message: Optional[str] = Field(None, max_length=500)
    
    @validator('access_level')
    def validate_access_level(cls, v):
        """Validate access level."""
        allowed_levels = ["view", "download"]
        if v not in allowed_levels:
            raise ValueError(f"Access level must be one of: {', '.join(allowed_levels)}")
        return v
