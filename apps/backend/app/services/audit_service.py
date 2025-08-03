"""
Comprehensive audit logging service for security and compliance.

Tracks all significant user actions, security events, and system changes
for security monitoring, compliance, and forensic analysis.
"""

import json
import hashlib
from datetime import datetime, timezone
from typing import Dict, Any, Optional, List
from enum import Enum
from dataclasses import dataclass, asdict
from sqlalchemy.orm import Session
from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, JSON, Index
from sqlalchemy.ext.declarative import declarative_base

from app.core.config import settings
from app.core.logging_config import get_logger
from app.db.base import Base

logger = get_logger(__name__)


class AuditEventType(str, Enum):
    """Types of audit events."""
    # Authentication events
    LOGIN_SUCCESS = "login_success"
    LOGIN_FAILURE = "login_failure"
    LOGOUT = "logout"
    PASSWORD_CHANGE = "password_change"
    PASSWORD_RESET_REQUEST = "password_reset_request"
    PASSWORD_RESET_COMPLETE = "password_reset_complete"
    ACCOUNT_LOCKED = "account_locked"
    ACCOUNT_UNLOCKED = "account_unlocked"
    
    # Authorization events
    ACCESS_GRANTED = "access_granted"
    ACCESS_DENIED = "access_denied"
    ROLE_CHANGE = "role_change"
    PERMISSION_CHANGE = "permission_change"
    
    # Data events
    USER_CREATED = "user_created"
    USER_UPDATED = "user_updated"
    USER_DELETED = "user_deleted"
    PROJECT_CREATED = "project_created"
    PROJECT_UPDATED = "project_updated"
    PROJECT_DELETED = "project_deleted"
    CALCULATION_CREATED = "calculation_created"
    CALCULATION_UPDATED = "calculation_updated"
    CALCULATION_DELETED = "calculation_deleted"
    REPORT_GENERATED = "report_generated"
    REPORT_DOWNLOADED = "report_downloaded"
    FILE_UPLOADED = "file_uploaded"
    FILE_DOWNLOADED = "file_downloaded"
    FILE_DELETED = "file_deleted"
    
    # System events
    CONFIGURATION_CHANGE = "configuration_change"
    SYSTEM_BACKUP = "system_backup"
    SYSTEM_RESTORE = "system_restore"
    MAINTENANCE_START = "maintenance_start"
    MAINTENANCE_END = "maintenance_end"
    
    # Security events
    SUSPICIOUS_ACTIVITY = "suspicious_activity"
    BRUTE_FORCE_ATTEMPT = "brute_force_attempt"
    SQL_INJECTION_ATTEMPT = "sql_injection_attempt"
    XSS_ATTEMPT = "xss_attempt"
    UNAUTHORIZED_API_ACCESS = "unauthorized_api_access"
    DATA_EXPORT = "data_export"
    BULK_OPERATION = "bulk_operation"
    
    # Admin events
    ADMIN_LOGIN = "admin_login"
    ADMIN_ACTION = "admin_action"
    USER_IMPERSONATION = "user_impersonation"


class AuditSeverity(str, Enum):
    """Severity levels for audit events."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class AuditContext:
    """Context information for audit events."""
    user_id: Optional[int] = None
    organization_id: Optional[int] = None
    session_id: Optional[str] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    request_id: Optional[str] = None
    api_endpoint: Optional[str] = None
    http_method: Optional[str] = None


class AuditLog(Base):
    """Audit log table for storing security and compliance events."""
    __tablename__ = "audit_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Event identification
    event_type = Column(String(100), nullable=False, index=True)
    event_category = Column(String(50), nullable=False, index=True)
    severity = Column(String(20), nullable=False, index=True)
    
    # Timing
    timestamp = Column(DateTime(timezone=True), nullable=False, index=True)
    
    # User and context
    user_id = Column(Integer, index=True, nullable=True)
    organization_id = Column(Integer, index=True, nullable=True)
    session_id = Column(String(255), index=True, nullable=True)
    
    # Request context
    ip_address = Column(String(45), index=True, nullable=True)  # IPv6 support
    user_agent = Column(Text, nullable=True)
    request_id = Column(String(255), index=True, nullable=True)
    api_endpoint = Column(String(255), index=True, nullable=True)
    http_method = Column(String(10), nullable=True)
    
    # Event details
    description = Column(Text, nullable=False)
    details = Column(JSON, nullable=True)
    
    # Resource information
    resource_type = Column(String(100), index=True, nullable=True)
    resource_id = Column(String(100), index=True, nullable=True)
    
    # Security
    checksum = Column(String(64), nullable=False)  # SHA-256 hash for integrity
    
    # Status
    is_sensitive = Column(Boolean, default=False, nullable=False)
    requires_investigation = Column(Boolean, default=False, nullable=False)
    
    # Indexes for performance
    __table_args__ = (
        Index('idx_audit_user_time', 'user_id', 'timestamp'),
        Index('idx_audit_org_time', 'organization_id', 'timestamp'),
        Index('idx_audit_event_time', 'event_type', 'timestamp'),
        Index('idx_audit_severity_time', 'severity', 'timestamp'),
        Index('idx_audit_ip_time', 'ip_address', 'timestamp'),
        Index('idx_audit_investigation', 'requires_investigation', 'timestamp'),
    )


class AuditService:
    """Comprehensive audit logging service."""
    
    def __init__(self):
        self.logger = get_logger('vessel_guard.audit')
    
    def log_event(
        self,
        db: Session,
        event_type: AuditEventType,
        description: str,
        context: AuditContext,
        severity: AuditSeverity = AuditSeverity.MEDIUM,
        details: Optional[Dict[str, Any]] = None,
        resource_type: Optional[str] = None,
        resource_id: Optional[str] = None,
        is_sensitive: bool = False,
        requires_investigation: bool = False
    ) -> AuditLog:
        """Log an audit event."""
        try:
            # Determine event category
            event_category = self._categorize_event(event_type)
            
            # Create audit log entry
            audit_entry = AuditLog(
                event_type=event_type.value,
                event_category=event_category,
                severity=severity.value,
                timestamp=datetime.now(timezone.utc),
                user_id=context.user_id,
                organization_id=context.organization_id,
                session_id=context.session_id,
                ip_address=context.ip_address,
                user_agent=context.user_agent,
                request_id=context.request_id,
                api_endpoint=context.api_endpoint,
                http_method=context.http_method,
                description=description,
                details=details,
                resource_type=resource_type,
                resource_id=resource_id,
                is_sensitive=is_sensitive,
                requires_investigation=requires_investigation
            )
            
            # Calculate checksum for integrity
            audit_entry.checksum = self._calculate_checksum(audit_entry)
            
            # Save to database
            db.add(audit_entry)
            db.commit()
            db.refresh(audit_entry)
            
            # Log to application logs for immediate visibility
            log_level = self._get_log_level(severity)
            self.logger.log(
                log_level,
                f"AUDIT: {event_type.value} - {description}",
                extra={
                    "audit_id": audit_entry.id,
                    "event_type": event_type.value,
                    "severity": severity.value,
                    "user_id": context.user_id,
                    "organization_id": context.organization_id,
                    "ip_address": context.ip_address,
                    "resource_type": resource_type,
                    "resource_id": resource_id
                }
            )
            
            # Check for security alerts
            if severity in [AuditSeverity.HIGH, AuditSeverity.CRITICAL]:
                self._trigger_security_alert(audit_entry)
            
            return audit_entry
            
        except Exception as e:
            self.logger.error(f"Failed to log audit event: {e}")
            raise
    
    def log_authentication_event(
        self,
        db: Session,
        event_type: AuditEventType,
        user_id: Optional[int],
        email: str,
        success: bool,
        context: AuditContext,
        failure_reason: Optional[str] = None
    ) -> AuditLog:
        """Log authentication-related events."""
        description = f"Authentication attempt for {email}"
        if not success and failure_reason:
            description += f" - {failure_reason}"
        
        severity = AuditSeverity.LOW if success else AuditSeverity.MEDIUM
        requires_investigation = not success
        
        details = {
            "email": email,
            "success": success,
            "failure_reason": failure_reason
        }
        
        return self.log_event(
            db=db,
            event_type=event_type,
            description=description,
            context=context,
            severity=severity,
            details=details,
            requires_investigation=requires_investigation
        )
    
    def log_data_access(
        self,
        db: Session,
        user_id: int,
        action: str,
        resource_type: str,
        resource_id: str,
        context: AuditContext,
        additional_data: Optional[Dict[str, Any]] = None
    ) -> AuditLog:
        """Log data access events."""
        description = f"User {user_id} {action} {resource_type} {resource_id}"
        
        details = {
            "action": action,
            "resource_type": resource_type,
            "resource_id": resource_id
        }
        if additional_data:
            details.update(additional_data)
        
        # Determine event type based on action
        event_type_map = {
            "created": AuditEventType.PROJECT_CREATED,
            "updated": AuditEventType.PROJECT_UPDATED,
            "deleted": AuditEventType.PROJECT_DELETED,
            "viewed": AuditEventType.ACCESS_GRANTED,
            "downloaded": AuditEventType.FILE_DOWNLOADED
        }
        
        event_type = event_type_map.get(action, AuditEventType.ACCESS_GRANTED)
        
        return self.log_event(
            db=db,
            event_type=event_type,
            description=description,
            context=context,
            severity=AuditSeverity.LOW,
            details=details,
            resource_type=resource_type,
            resource_id=resource_id
        )
    
    def log_security_event(
        self,
        db: Session,
        event_type: AuditEventType,
        description: str,
        context: AuditContext,
        threat_details: Dict[str, Any],
        severity: AuditSeverity = AuditSeverity.HIGH
    ) -> AuditLog:
        """Log security-related events."""
        return self.log_event(
            db=db,
            event_type=event_type,
            description=description,
            context=context,
            severity=severity,
            details=threat_details,
            is_sensitive=True,
            requires_investigation=True
        )
    
    def log_admin_action(
        self,
        db: Session,
        admin_user_id: int,
        action: str,
        target_resource: str,
        context: AuditContext,
        details: Optional[Dict[str, Any]] = None
    ) -> AuditLog:
        """Log administrative actions."""
        description = f"Admin {admin_user_id} performed {action} on {target_resource}"
        
        return self.log_event(
            db=db,
            event_type=AuditEventType.ADMIN_ACTION,
            description=description,
            context=context,
            severity=AuditSeverity.MEDIUM,
            details=details,
            is_sensitive=True
        )
    
    def get_audit_trail(
        self,
        db: Session,
        user_id: Optional[int] = None,
        organization_id: Optional[int] = None,
        resource_type: Optional[str] = None,
        resource_id: Optional[str] = None,
        event_types: Optional[List[str]] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        severity: Optional[AuditSeverity] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[AuditLog]:
        """Retrieve audit trail with filtering."""
        try:
            query = db.query(AuditLog)
            
            # Apply filters
            if user_id:
                query = query.filter(AuditLog.user_id == user_id)
            
            if organization_id:
                query = query.filter(AuditLog.organization_id == organization_id)
            
            if resource_type:
                query = query.filter(AuditLog.resource_type == resource_type)
            
            if resource_id:
                query = query.filter(AuditLog.resource_id == resource_id)
            
            if event_types:
                query = query.filter(AuditLog.event_type.in_(event_types))
            
            if start_date:
                query = query.filter(AuditLog.timestamp >= start_date)
            
            if end_date:
                query = query.filter(AuditLog.timestamp <= end_date)
            
            if severity:
                query = query.filter(AuditLog.severity == severity.value)
            
            # Order by timestamp (most recent first)
            query = query.order_by(AuditLog.timestamp.desc())
            
            # Apply pagination
            query = query.offset(offset).limit(limit)
            
            return query.all()
            
        except Exception as e:
            self.logger.error(f"Failed to retrieve audit trail: {e}")
            return []
    
    def get_security_alerts(
        self,
        db: Session,
        hours: int = 24,
        limit: int = 50
    ) -> List[AuditLog]:
        """Get recent security alerts requiring investigation."""
        try:
            from datetime import timedelta
            
            cutoff_time = datetime.now(timezone.utc) - timedelta(hours=hours)
            
            return (
                db.query(AuditLog)
                .filter(
                    AuditLog.requires_investigation == True,
                    AuditLog.timestamp >= cutoff_time
                )
                .order_by(AuditLog.timestamp.desc())
                .limit(limit)
                .all()
            )
            
        except Exception as e:
            self.logger.error(f"Failed to retrieve security alerts: {e}")
            return []
    
    def verify_audit_integrity(
        self,
        db: Session,
        audit_log: AuditLog
    ) -> bool:
        """Verify the integrity of an audit log entry."""
        try:
            calculated_checksum = self._calculate_checksum(audit_log)
            return calculated_checksum == audit_log.checksum
            
        except Exception as e:
            self.logger.error(f"Failed to verify audit integrity: {e}")
            return False
    
    def _categorize_event(self, event_type: AuditEventType) -> str:
        """Categorize event types for easier filtering."""
        auth_events = [
            AuditEventType.LOGIN_SUCCESS, AuditEventType.LOGIN_FAILURE,
            AuditEventType.LOGOUT, AuditEventType.PASSWORD_CHANGE,
            AuditEventType.PASSWORD_RESET_REQUEST, AuditEventType.PASSWORD_RESET_COMPLETE,
            AuditEventType.ACCOUNT_LOCKED, AuditEventType.ACCOUNT_UNLOCKED
        ]
        
        data_events = [
            AuditEventType.USER_CREATED, AuditEventType.USER_UPDATED, AuditEventType.USER_DELETED,
            AuditEventType.PROJECT_CREATED, AuditEventType.PROJECT_UPDATED, AuditEventType.PROJECT_DELETED,
            AuditEventType.CALCULATION_CREATED, AuditEventType.CALCULATION_UPDATED, AuditEventType.CALCULATION_DELETED,
            AuditEventType.REPORT_GENERATED, AuditEventType.REPORT_DOWNLOADED,
            AuditEventType.FILE_UPLOADED, AuditEventType.FILE_DOWNLOADED, AuditEventType.FILE_DELETED
        ]
        
        security_events = [
            AuditEventType.SUSPICIOUS_ACTIVITY, AuditEventType.BRUTE_FORCE_ATTEMPT,
            AuditEventType.SQL_INJECTION_ATTEMPT, AuditEventType.XSS_ATTEMPT,
            AuditEventType.UNAUTHORIZED_API_ACCESS, AuditEventType.ACCESS_DENIED
        ]
        
        admin_events = [
            AuditEventType.ADMIN_LOGIN, AuditEventType.ADMIN_ACTION,
            AuditEventType.USER_IMPERSONATION, AuditEventType.ROLE_CHANGE,
            AuditEventType.PERMISSION_CHANGE, AuditEventType.CONFIGURATION_CHANGE
        ]
        
        if event_type in auth_events:
            return "authentication"
        elif event_type in data_events:
            return "data"
        elif event_type in security_events:
            return "security"
        elif event_type in admin_events:
            return "admin"
        else:
            return "system"
    
    def _calculate_checksum(self, audit_entry: AuditLog) -> str:
        """Calculate SHA-256 checksum for audit entry integrity."""
        # Create a string representation of the audit entry
        data = {
            "event_type": audit_entry.event_type,
            "timestamp": audit_entry.timestamp.isoformat() if audit_entry.timestamp else "",
            "user_id": audit_entry.user_id,
            "description": audit_entry.description,
            "details": json.dumps(audit_entry.details, sort_keys=True) if audit_entry.details else "",
            "resource_type": audit_entry.resource_type,
            "resource_id": audit_entry.resource_id
        }
        
        # Create deterministic string
        data_string = json.dumps(data, sort_keys=True)
        
        # Calculate SHA-256 hash
        return hashlib.sha256(data_string.encode()).hexdigest()
    
    def _get_log_level(self, severity: AuditSeverity) -> int:
        """Convert audit severity to logging level."""
        import logging
        
        level_map = {
            AuditSeverity.LOW: logging.INFO,
            AuditSeverity.MEDIUM: logging.WARNING,
            AuditSeverity.HIGH: logging.ERROR,
            AuditSeverity.CRITICAL: logging.CRITICAL
        }
        
        return level_map.get(severity, logging.INFO)
    
    def _trigger_security_alert(self, audit_entry: AuditLog):
        """Trigger security alert for high/critical severity events."""
        try:
            # In a production environment, this would:
            # 1. Send alerts to security team
            # 2. Update SIEM systems
            # 3. Trigger automated responses
            # 4. Create tickets in incident management systems
            
            self.logger.critical(
                f"SECURITY ALERT: {audit_entry.event_type} - {audit_entry.description}",
                extra={
                    "audit_id": audit_entry.id,
                    "severity": audit_entry.severity,
                    "user_id": audit_entry.user_id,
                    "ip_address": audit_entry.ip_address,
                    "requires_investigation": audit_entry.requires_investigation
                }
            )
            
        except Exception as e:
            self.logger.error(f"Failed to trigger security alert: {e}")


# Global audit service instance
audit_service = AuditService()