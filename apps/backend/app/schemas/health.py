"""
Health check schemas for monitoring and status reporting.

Defines data models for health check responses across different
system components and service dependencies.
"""

from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Any

from pydantic import BaseModel, Field


class HealthStatus(str, Enum):
    """Health status enumeration."""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"


class DatabaseHealth(BaseModel):
    """Database health status."""
    status: HealthStatus
    connection_time: Optional[float] = Field(None, description="Connection time in milliseconds")
    table_count: Optional[int] = Field(None, description="Number of database tables")
    last_check: datetime
    error: Optional[str] = None
    details: Dict[str, Any] = Field(default_factory=dict)

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class SystemHealth(BaseModel):
    """System resource health status."""
    status: HealthStatus
    cpu_percent: Optional[float] = Field(None, description="CPU usage percentage")
    memory_percent: Optional[float] = Field(None, description="Memory usage percentage")
    disk_percent: Optional[float] = Field(None, description="Disk usage percentage")
    uptime_seconds: int = Field(description="System uptime in seconds")
    last_check: datetime
    error: Optional[str] = None
    details: Dict[str, Any] = Field(default_factory=dict)

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class ServiceHealth(BaseModel):
    """External service health status."""
    name: str = Field(description="Service name")
    status: HealthStatus
    response_time: Optional[float] = Field(None, description="Response time in milliseconds")
    last_check: datetime
    endpoint: Optional[str] = Field(None, description="Service endpoint URL")
    error: Optional[str] = None
    details: Dict[str, Any] = Field(default_factory=dict)

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class DetailedHealthResponse(BaseModel):
    """Comprehensive health check response."""
    status: HealthStatus = Field(description="Overall system health status")
    timestamp: datetime = Field(description="Health check timestamp")
    service: str = Field(description="Service name")
    version: str = Field(description="Service version")
    uptime_seconds: int = Field(description="Service uptime in seconds")
    
    # Component health
    database: DatabaseHealth = Field(description="Database health status")
    system: SystemHealth = Field(description="System resource health")
    external_services: List[ServiceHealth] = Field(
        default_factory=list, 
        description="External service dependencies"
    )
    
    # Summary statistics
    summary: Dict[str, int] = Field(
        default_factory=dict,
        description="Health check summary statistics"
    )

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class BasicHealthResponse(BaseModel):
    """Basic health check response."""
    status: str = Field(description="Basic health status")
    timestamp: datetime = Field(description="Health check timestamp")
    service: str = Field(description="Service name")
    version: str = Field(description="Service version")

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class ReadinessResponse(BaseModel):
    """Readiness check response for Kubernetes."""
    status: str = Field(description="Readiness status")
    timestamp: datetime = Field(description="Check timestamp")
    checks: Dict[str, str] = Field(description="Individual readiness checks")

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class LivenessResponse(BaseModel):
    """Liveness check response for Kubernetes."""
    status: str = Field(description="Liveness status")
    timestamp: datetime = Field(description="Check timestamp")
    uptime_seconds: int = Field(description="Service uptime in seconds")

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class MetricsResponse(BaseModel):
    """Health metrics response for monitoring systems."""
    timestamp: datetime = Field(description="Metrics timestamp")
    response_time_seconds: float = Field(description="Health check response time")
    database_response_time_seconds: float = Field(description="Database response time")
    uptime_seconds: int = Field(description="Service uptime")
    status: str = Field(description="Overall status")
    cpu_percent: Optional[float] = Field(None, description="CPU usage percentage")
    memory_percent: Optional[float] = Field(None, description="Memory usage percentage")

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
