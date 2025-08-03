"""
Audit logging system for security and compliance tracking.

Provides comprehensive audit trails for all user actions,
data modifications, and system events.
"""

import json
from datetime import datetime
from typing import Any, Dict, Optional, Union, List
from enum import Enum
from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import Session, relationship
from sqlalchemy.sql import func

from app.db.base import Base
from app.core.logging_config import get_logger

logger = get_logger(__name__)


class AuditAction(str, Enum):
    """Types of actions that can be audited."""
    CREATE = "create"
    READ = "read"
    UPDATE = "update"
    DELETE = "delete"
    LOGIN = "login"
    LOGOUT = "logout"
    LOGIN_FAILED = "login_failed"
    PASSWORD_CHANGE = "password_change"
    PASSWORD_RESET = "password_reset"
    PERMISSION_GRANT = "permission_grant"
    PERMISSION_REVOKE = "permission_revoke"
    ROLE_CHANGE = "role_change"
    ACCOUNT_LOCK = "account_lock"
    ACCOUNT_UNLOCK = "account_unlock"
    CALCULATION_EXECUTE = "calculation_execute"
    REPORT_GENERATE = "report_generate"
    FILE_UPLOAD = "file_upload"
    FILE_DOWNLOAD = "file_download"
    FILE_DELETE = "file_delete"
    EXPORT_DATA = "export_data"
    IMPORT_DATA = "import_data"
    SYSTEM_CONFIG_CHANGE = "system_config_change"
    BACKUP_CREATE = "backup_create"
    BACKUP_RESTORE = "backup_restore"


class AuditSeverity(str, Enum):
    """Severity levels for audit events."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class AuditLog(Base):
    """
    Audit log model for tracking all user actions and system events.
    """
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    
    # Event identification
    action = Column(SQLEnum(AuditAction), nullable=False, index=True)
    severity = Column(SQLEnum(AuditSeverity), nullable=False, default=AuditSeverity.LOW)
    description = Column(String(500), nullable=False)
    
    # User and session information
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    session_id = Column(String(255), nullable=True, index=True)
    ip_address = Column(String(45), nullable=True)  # IPv6 compatible
    user_agent = Column(Text, nullable=True)
    
    # Resource information
    resource_type = Column(String(100), nullable=True, index=True)
    resource_id = Column(String(100), nullable=True, index=True)
    resource_name = Column(String(255), nullable=True)
    
    # Organization context
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=True, index=True)
    
    # Change tracking
    old_values = Column(Text, nullable=True)  # JSON string
    new_values = Column(Text, nullable=True)  # JSON string
    
    # Request information
    request_id = Column(String(255), nullable=True, index=True)
    endpoint = Column(String(255), nullable=True)
    method = Column(String(10), nullable=True)
    
    # Result information
    success = Column(String(10), nullable=False, default="true")  # true/false/error
    error_message = Column(Text, nullable=True)
    
    # Timing
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    duration_ms = Column(Integer, nullable=True)
    
    # Additional context
    additional_data = Column(Text, nullable=True)  # JSON string for extra context
    
    # Relationships
    user = relationship("User", back_populates="audit_logs")
    organization = relationship("Organization")

    def __repr__(self) -> str:
        return f"<AuditLog(id={self.id}, action={self.action}, user_id={self.user_id})>"


class AuditService:
    """Service for creating and managing audit logs."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def log_event(
        self,
        action: AuditAction,
        description: str,
        user_id: Optional[int] = None,
        session_id: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        resource_type: Optional[str] = None,
        resource_id: Optional[Union[str, int]] = None,
        resource_name: Optional[str] = None,
        organization_id: Optional[int] = None,
        old_values: Optional[Dict[str, Any]] = None,
        new_values: Optional[Dict[str, Any]] = None,
        request_id: Optional[str] = None,
        endpoint: Optional[str] = None,
        method: Optional[str] = None,
        success: bool = True,
        error_message: Optional[str] = None,
        duration_ms: Optional[int] = None,
        severity: AuditSeverity = AuditSeverity.LOW,
        additional_data: Optional[Dict[str, Any]] = None
    ) -> AuditLog:
        """
        Create an audit log entry.
        
        Args:
            action: The action being performed
            description: Human-readable description of the action
            user_id: ID of the user performing the action
            session_id: Session identifier
            ip_address: IP address of the client
            user_agent: User agent string
            resource_type: Type of resource being acted upon
            resource_id: ID of the resource
            resource_name: Name/title of the resource
            organization_id: Organization context
            old_values: Previous values (for updates)
            new_values: New values (for creates/updates)
            request_id: Unique request identifier
            endpoint: API endpoint
            method: HTTP method
            success: Whether the action was successful
            error_message: Error message if action failed
            duration_ms: Duration of the action in milliseconds
            severity: Severity level of the event
            additional_data: Additional context data
            
        Returns:
            Created AuditLog instance
        """
        try:
            audit_log = AuditLog(
                action=action,
                severity=severity,
                description=description,
                user_id=user_id,
                session_id=session_id,
                ip_address=ip_address,
                user_agent=user_agent,
                resource_type=resource_type,
                resource_id=str(resource_id) if resource_id is not None else None,
                resource_name=resource_name,
                organization_id=organization_id,
                old_values=json.dumps(old_values) if old_values else None,
                new_values=json.dumps(new_values) if new_values else None,
                request_id=request_id,
                endpoint=endpoint,
                method=method,
                success="true" if success else ("false" if not error_message else "error"),
                error_message=error_message,
                duration_ms=duration_ms,
                additional_data=json.dumps(additional_data) if additional_data else None
            )
            
            self.db.add(audit_log)
            self.db.commit()
            self.db.refresh(audit_log)
            
            # Also log to application logger for immediate visibility
            log_level = "ERROR" if not success else ("WARNING" if severity in [AuditSeverity.HIGH, AuditSeverity.CRITICAL] else "INFO")
            logger.log(
                getattr(logger, log_level.lower()),
                f"AUDIT: {action.value} - {description} "
                f"(user_id={user_id}, resource={resource_type}:{resource_id}, "
                f"success={success})"
            )
            
            return audit_log
            
        except Exception as e:
            logger.error(f"Failed to create audit log: {e}")
            # Don't let audit logging failures break the application
            self.db.rollback()
            return None
    
    def log_authentication(
        self,
        user_id: Optional[int],
        action: AuditAction,
        ip_address: str,
        user_agent: str,
        success: bool = True,
        error_message: Optional[str] = None,
        session_id: Optional[str] = None
    ):
        """Log authentication-related events."""
        severity = AuditSeverity.MEDIUM if action == AuditAction.LOGIN_FAILED else AuditSeverity.LOW
        
        self.log_event(
            action=action,
            description=f"User authentication: {action.value}",
            user_id=user_id,
            session_id=session_id,
            ip_address=ip_address,
            user_agent=user_agent,
            success=success,
            error_message=error_message,
            severity=severity
        )
    
    def log_data_change(
        self,
        action: AuditAction,
        resource_type: str,
        resource_id: Union[str, int],
        resource_name: str,
        user_id: int,
        organization_id: int,
        old_values: Optional[Dict[str, Any]] = None,
        new_values: Optional[Dict[str, Any]] = None,
        request_id: Optional[str] = None
    ):
        """Log data creation, modification, or deletion."""
        action_map = {
            AuditAction.CREATE: "created",
            AuditAction.UPDATE: "updated", 
            AuditAction.DELETE: "deleted"
        }
        
        description = f"{resource_type} '{resource_name}' {action_map.get(action, action.value)}"
        
        self.log_event(
            action=action,
            description=description,
            user_id=user_id,
            resource_type=resource_type,
            resource_id=resource_id,
            resource_name=resource_name,
            organization_id=organization_id,
            old_values=old_values,
            new_values=new_values,
            request_id=request_id,
            severity=AuditSeverity.MEDIUM if action == AuditAction.DELETE else AuditSeverity.LOW
        )
    
    def log_permission_change(
        self,
        target_user_id: int,
        changed_by_user_id: int,
        action: AuditAction,
        details: Dict[str, Any],
        organization_id: int
    ):
        """Log permission and role changes."""
        self.log_event(
            action=action,
            description=f"User permissions modified: {action.value}",
            user_id=changed_by_user_id,
            resource_type="user",
            resource_id=target_user_id,
            organization_id=organization_id,
            new_values=details,
            severity=AuditSeverity.HIGH
        )
    
    def log_calculation(
        self,
        calculation_id: int,
        calculation_type: str,
        user_id: int,
        organization_id: int,
        input_data: Dict[str, Any],
        result_data: Dict[str, Any],
        success: bool = True,
        error_message: Optional[str] = None
    ):
        """Log engineering calculations."""
        self.log_event(
            action=AuditAction.CALCULATION_EXECUTE,
            description=f"Engineering calculation performed: {calculation_type}",
            user_id=user_id,
            resource_type="calculation",
            resource_id=calculation_id,
            organization_id=organization_id,
            new_values={"input": input_data, "result": result_data},
            success=success,
            error_message=error_message,
            severity=AuditSeverity.MEDIUM
        )
    
    def log_file_operation(
        self,
        action: AuditAction,
        file_name: str,
        file_path: str,
        user_id: int,
        organization_id: int,
        file_size: Optional[int] = None,
        file_type: Optional[str] = None
    ):
        """Log file upload, download, or deletion operations."""
        additional_data = {
            "file_path": file_path,
            "file_size": file_size,
            "file_type": file_type
        }
        
        self.log_event(
            action=action,
            description=f"File operation: {action.value} - {file_name}",
            user_id=user_id,
            resource_type="file",
            resource_name=file_name,
            organization_id=organization_id,
            additional_data=additional_data,
            severity=AuditSeverity.MEDIUM if action == AuditAction.FILE_DELETE else AuditSeverity.LOW
        )
    
    def get_user_activity(
        self,
        user_id: int,
        days: int = 30,
        actions: Optional[List[AuditAction]] = None
    ) -> List[AuditLog]:
        """Get recent activity for a user."""
        query = self.db.query(AuditLog).filter(AuditLog.user_id == user_id)
        
        if actions:
            query = query.filter(AuditLog.action.in_(actions))
        
        # Last N days
        from datetime import timedelta
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        query = query.filter(AuditLog.timestamp >= cutoff_date)
        
        return query.order_by(AuditLog.timestamp.desc()).limit(1000).all()
    
    def get_resource_history(
        self,
        resource_type: str,
        resource_id: Union[str, int],
        organization_id: Optional[int] = None
    ) -> List[AuditLog]:
        """Get audit history for a specific resource."""
        query = self.db.query(AuditLog).filter(
            AuditLog.resource_type == resource_type,
            AuditLog.resource_id == str(resource_id)
        )
        
        if organization_id:
            query = query.filter(AuditLog.organization_id == organization_id)
        
        return query.order_by(AuditLog.timestamp.desc()).all()
    
    def get_security_events(
        self,
        days: int = 7,
        severity: Optional[AuditSeverity] = None
    ) -> List[AuditLog]:
        """Get recent security-related events."""
        security_actions = [
            AuditAction.LOGIN_FAILED,
            AuditAction.ACCOUNT_LOCK,
            AuditAction.PERMISSION_GRANT,
            AuditAction.PERMISSION_REVOKE,
            AuditAction.ROLE_CHANGE,
            AuditAction.PASSWORD_CHANGE,
            AuditAction.PASSWORD_RESET
        ]
        
        query = self.db.query(AuditLog).filter(AuditLog.action.in_(security_actions))
        
        if severity:
            query = query.filter(AuditLog.severity == severity)
        
        # Last N days
        from datetime import timedelta
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        query = query.filter(AuditLog.timestamp >= cutoff_date)
        
        return query.order_by(AuditLog.timestamp.desc()).limit(500).all()


def log_audit_event(
    db: Session,
    action: AuditAction,
    description: str,
    **kwargs
) -> Optional[AuditLog]:
    """
    Convenience function to log audit events.
    
    Usage:
        log_audit_event(
            db=db,
            action=AuditAction.CREATE,
            description="Created new project",
            user_id=current_user.id,
            resource_type="project",
            resource_id=project.id
        )
    """
    audit_service = AuditService(db)
    return audit_service.log_event(action, description, **kwargs)
