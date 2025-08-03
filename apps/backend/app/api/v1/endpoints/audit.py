"""
Audit and security monitoring endpoints.

Provides access to audit logs, security events, and compliance
reporting for administrators and security teams.
"""

from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.api.dependencies import get_current_user, get_db, require_role
from app.db.models.user import User, UserRole
from app.services.audit_service import (
    audit_service, 
    AuditLog, 
    AuditEventType, 
    AuditSeverity, 
    AuditContext
)
from app.core.logging_config import get_logger

logger = get_logger(__name__)
router = APIRouter()


class AuditLogResponse(BaseModel):
    """Audit log response model."""
    id: int
    event_type: str
    event_category: str
    severity: str
    timestamp: datetime
    user_id: Optional[int]
    organization_id: Optional[int]
    session_id: Optional[str]
    ip_address: Optional[str]
    user_agent: Optional[str]
    api_endpoint: Optional[str]
    http_method: Optional[str]
    description: str
    details: Optional[Dict[str, Any]]
    resource_type: Optional[str]
    resource_id: Optional[str]
    is_sensitive: bool
    requires_investigation: bool

    class Config:
        from_attributes = True


class AuditSummaryResponse(BaseModel):
    """Audit summary response model."""
    total_events: int
    events_by_severity: Dict[str, int]
    events_by_category: Dict[str, int]
    recent_security_events: int
    failed_logins_24h: int
    suspicious_activities: int
    top_users_by_activity: List[Dict[str, Any]]
    top_source_ips: List[Dict[str, Any]]


class SecurityAlertResponse(BaseModel):
    """Security alert response model."""
    id: int
    event_type: str
    severity: str
    timestamp: datetime
    description: str
    ip_address: Optional[str]
    user_id: Optional[int]
    requires_investigation: bool
    details: Optional[Dict[str, Any]]

    class Config:
        from_attributes = True


@router.get("/logs", response_model=List[AuditLogResponse])
async def get_audit_logs(
    user_id: Optional[int] = Query(None, description="Filter by user ID"),
    organization_id: Optional[int] = Query(None, description="Filter by organization ID"),
    event_type: Optional[str] = Query(None, description="Filter by event type"),
    severity: Optional[str] = Query(None, description="Filter by severity"),
    start_date: Optional[datetime] = Query(None, description="Start date for filtering"),
    end_date: Optional[datetime] = Query(None, description="End date for filtering"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records"),
    offset: int = Query(0, ge=0, description="Number of records to skip"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role([UserRole.ENGINEER]))
):
    """
    Get audit logs with filtering options.
    
    Requires engineer role to access audit logs.
    """
    try:
        # Convert severity string to enum if provided
        severity_enum = None
        if severity:
            try:
                severity_enum = AuditSeverity(severity)
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid severity value: {severity}"
                )
        
        # Get audit trail
        audit_logs = audit_service.get_audit_trail(
            db=db,
            user_id=user_id,
            organization_id=organization_id,
            event_types=[event_type] if event_type else None,
            start_date=start_date,
            end_date=end_date,
            severity=severity_enum,
            limit=limit,
            offset=offset
        )
        
        return audit_logs
        
    except Exception as e:
        logger.error(f"Failed to retrieve audit logs: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve audit logs"
        )


@router.get("/logs/{log_id}", response_model=AuditLogResponse)
async def get_audit_log(
    log_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role([UserRole.ENGINEER]))
):
    """Get a specific audit log entry by ID."""
    try:
        audit_log = db.query(AuditLog).filter(AuditLog.id == log_id).first()
        
        if not audit_log:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Audit log not found"
            )
        
        # Verify integrity
        if not audit_service.verify_audit_integrity(db, audit_log):
            logger.warning(f"Audit log integrity check failed for ID: {log_id}")
        
        return audit_log
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to retrieve audit log {log_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve audit log"
        )


@router.get("/summary", response_model=AuditSummaryResponse)
async def get_audit_summary(
    days: int = Query(30, ge=1, le=365, description="Number of days to analyze"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role([UserRole.ENGINEER]))
):
    """Get audit summary and statistics."""
    try:
        # Calculate date range
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        # Get audit logs for the period
        audit_logs = audit_service.get_audit_trail(
            db=db,
            start_date=start_date,
            end_date=end_date,
            limit=10000  # Large limit for analysis
        )
        
        # Calculate statistics
        total_events = len(audit_logs)
        
        # Events by severity
        events_by_severity = {}
        for severity in AuditSeverity:
            events_by_severity[severity.value] = sum(
                1 for log in audit_logs if log.severity == severity.value
            )
        
        # Events by category
        events_by_category = {}
        categories = set(log.event_category for log in audit_logs)
        for category in categories:
            events_by_category[category] = sum(
                1 for log in audit_logs if log.event_category == category
            )
        
        # Recent security events
        recent_security_events = sum(
            1 for log in audit_logs 
            if log.event_category == "security" and 
               log.timestamp >= end_date - timedelta(hours=24)
        )
        
        # Failed logins in last 24 hours
        failed_logins_24h = sum(
            1 for log in audit_logs 
            if log.event_type == AuditEventType.LOGIN_FAILURE.value and
               log.timestamp >= end_date - timedelta(hours=24)
        )
        
        # Suspicious activities
        suspicious_activities = sum(
            1 for log in audit_logs 
            if log.requires_investigation
        )
        
        # Top users by activity
        user_activity = {}
        for log in audit_logs:
            if log.user_id:
                user_activity[log.user_id] = user_activity.get(log.user_id, 0) + 1
        
        top_users_by_activity = [
            {"user_id": user_id, "activity_count": count}
            for user_id, count in sorted(user_activity.items(), key=lambda x: x[1], reverse=True)[:10]
        ]
        
        # Top source IPs
        ip_activity = {}
        for log in audit_logs:
            if log.ip_address:
                ip_activity[log.ip_address] = ip_activity.get(log.ip_address, 0) + 1
        
        top_source_ips = [
            {"ip_address": ip, "request_count": count}
            for ip, count in sorted(ip_activity.items(), key=lambda x: x[1], reverse=True)[:10]
        ]
        
        return AuditSummaryResponse(
            total_events=total_events,
            events_by_severity=events_by_severity,
            events_by_category=events_by_category,
            recent_security_events=recent_security_events,
            failed_logins_24h=failed_logins_24h,
            suspicious_activities=suspicious_activities,
            top_users_by_activity=top_users_by_activity,
            top_source_ips=top_source_ips
        )
        
    except Exception as e:
        logger.error(f"Failed to generate audit summary: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate audit summary"
        )


@router.get("/security-alerts", response_model=List[SecurityAlertResponse])
async def get_security_alerts(
    hours: int = Query(24, ge=1, le=168, description="Hours to look back"),
    limit: int = Query(50, ge=1, le=500, description="Maximum number of alerts"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role([UserRole.ENGINEER]))
):
    """Get recent security alerts requiring investigation."""
    try:
        security_alerts = audit_service.get_security_alerts(
            db=db,
            hours=hours,
            limit=limit
        )
        
        return [
            SecurityAlertResponse(
                id=alert.id,
                event_type=alert.event_type,
                severity=alert.severity,
                timestamp=alert.timestamp,
                description=alert.description,
                ip_address=alert.ip_address,
                user_id=alert.user_id,
                requires_investigation=alert.requires_investigation,
                details=alert.details
            )
            for alert in security_alerts
        ]
        
    except Exception as e:
        logger.error(f"Failed to retrieve security alerts: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve security alerts"
        )


@router.post("/logs/{log_id}/investigate")
async def mark_for_investigation(
    log_id: int,
    investigation_note: str = Query(..., description="Investigation note"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role([UserRole.ENGINEER]))
):
    """Mark an audit log entry for investigation."""
    try:
        audit_log = db.query(AuditLog).filter(AuditLog.id == log_id).first()
        
        if not audit_log:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Audit log not found"
            )
        
        # Update investigation status
        audit_log.requires_investigation = True
        
        # Add investigation details
        if not audit_log.details:
            audit_log.details = {}
        
        audit_log.details["investigation"] = {
            "marked_by": current_user.id,
            "marked_at": datetime.utcnow().isoformat(),
            "note": investigation_note
        }
        
        db.commit()
        
        # Log the investigation action
        audit_context = AuditContext(
            user_id=current_user.id,
            organization_id=current_user.organization_id
        )
        
        audit_service.log_event(
            db=db,
            event_type=AuditEventType.ADMIN_ACTION,
            description=f"Audit log {log_id} marked for investigation",
            context=audit_context,
            severity=AuditSeverity.MEDIUM,
            details={
                "action": "mark_for_investigation",
                "target_log_id": log_id,
                "note": investigation_note
            }
        )
        
        return {"message": "Audit log marked for investigation", "log_id": log_id}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to mark audit log for investigation: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to mark audit log for investigation"
        )


@router.get("/user/{user_id}/activity", response_model=List[AuditLogResponse])
async def get_user_activity(
    user_id: int,
    days: int = Query(30, ge=1, le=365, description="Number of days to look back"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role([UserRole.ENGINEER]))
):
    """Get activity history for a specific user."""
    try:
        # Calculate date range
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        # Get user activity
        audit_logs = audit_service.get_audit_trail(
            db=db,
            user_id=user_id,
            start_date=start_date,
            end_date=end_date,
            limit=limit
        )
        
        return audit_logs
        
    except Exception as e:
        logger.error(f"Failed to retrieve user activity for user {user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve user activity"
        )


@router.get("/export")
async def export_audit_logs(
    start_date: datetime = Query(..., description="Start date for export"),
    end_date: datetime = Query(..., description="End date for export"),
    format: str = Query("json", regex="^(json|csv)$", description="Export format"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role([UserRole.ENGINEER]))
):
    """Export audit logs for compliance reporting."""
    try:
        # Limit export to reasonable timeframe
        if (end_date - start_date).days > 365:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Export timeframe cannot exceed 365 days"
            )
        
        # Get audit logs
        audit_logs = audit_service.get_audit_trail(
            db=db,
            start_date=start_date,
            end_date=end_date,
            limit=100000  # Large limit for export
        )
        
        # Log the export action
        audit_context = AuditContext(
            user_id=current_user.id,
            organization_id=current_user.organization_id
        )
        
        audit_service.log_event(
            db=db,
            event_type=AuditEventType.DATA_EXPORT,
            description=f"Audit logs exported by user {current_user.id}",
            context=audit_context,
            severity=AuditSeverity.MEDIUM,
            details={
                "export_format": format,
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
                "record_count": len(audit_logs)
            },
            is_sensitive=True
        )
        
        if format == "json":
            from fastapi.responses import JSONResponse
            return JSONResponse(
                content=[
                    {
                        "id": log.id,
                        "event_type": log.event_type,
                        "severity": log.severity,
                        "timestamp": log.timestamp.isoformat(),
                        "user_id": log.user_id,
                        "ip_address": log.ip_address,
                        "description": log.description,
                        "details": log.details
                    }
                    for log in audit_logs
                ],
                headers={"Content-Disposition": f"attachment; filename=audit_logs_{start_date.strftime('%Y%m%d')}_{end_date.strftime('%Y%m%d')}.json"}
            )
        
        elif format == "csv":
            import csv
            import io
            from fastapi.responses import StreamingResponse
            
            output = io.StringIO()
            writer = csv.writer(output)
            
            # Write header
            writer.writerow([
                "ID", "Event Type", "Severity", "Timestamp", "User ID", 
                "IP Address", "Description", "Details"
            ])
            
            # Write data
            for log in audit_logs:
                writer.writerow([
                    log.id,
                    log.event_type,
                    log.severity,
                    log.timestamp.isoformat(),
                    log.user_id,
                    log.ip_address,
                    log.description,
                    str(log.details) if log.details else ""
                ])
            
            output.seek(0)
            
            return StreamingResponse(
                io.BytesIO(output.getvalue().encode()),
                media_type="text/csv",
                headers={"Content-Disposition": f"attachment; filename=audit_logs_{start_date.strftime('%Y%m%d')}_{end_date.strftime('%Y%m%d')}.csv"}
            )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to export audit logs: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to export audit logs"
        )