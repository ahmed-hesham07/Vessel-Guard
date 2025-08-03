"""
Enhanced session management system.

Provides secure session tracking, timeout handling,
concurrent session limits, and session security features.
"""

import uuid
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Set
from enum import Enum
import json
from dataclasses import dataclass, asdict

from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, ForeignKey
from sqlalchemy.orm import Session, relationship
from sqlalchemy.sql import func
from redis import Redis
from fastapi import Request, HTTPException, status

from app.db.base import Base
from app.core.config import settings
from app.core.logging_config import get_logger
from app.core.audit import AuditAction, AuditService

logger = get_logger(__name__)


class SessionStatus(str, Enum):
    """Session status types."""
    ACTIVE = "active"
    EXPIRED = "expired"
    TERMINATED = "terminated"
    LOCKED = "locked"


class SessionType(str, Enum):
    """Session type classification."""
    WEB = "web"
    API = "api"
    MOBILE = "mobile"
    SYSTEM = "system"


@dataclass
class SessionInfo:
    """Session information data class."""
    session_id: str
    user_id: int
    session_type: SessionType
    ip_address: str
    user_agent: str
    created_at: datetime
    last_activity: datetime
    expires_at: datetime
    status: SessionStatus
    organization_id: Optional[int] = None
    device_fingerprint: Optional[str] = None
    location: Optional[str] = None
    is_trusted_device: bool = False
    concurrent_session_count: int = 0


class UserSession(Base):
    """
    Database model for tracking user sessions.
    """
    __tablename__ = "user_sessions"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(255), unique=True, nullable=False, index=True)
    
    # User information
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=True)
    
    # Session details
    session_type = Column(String(20), nullable=False, default=SessionType.WEB)
    status = Column(String(20), nullable=False, default=SessionStatus.ACTIVE)
    
    # Client information
    ip_address = Column(String(45), nullable=False)  # IPv6 compatible
    user_agent = Column(Text, nullable=True)
    device_fingerprint = Column(String(255), nullable=True, index=True)
    location = Column(String(255), nullable=True)
    is_trusted_device = Column(Boolean, default=False)
    
    # Timing
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    last_activity = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    terminated_at = Column(DateTime(timezone=True), nullable=True)
    
    # Security features
    login_method = Column(String(50), nullable=True)  # password, sso, mfa
    risk_score = Column(Integer, default=0)  # 0-100 risk assessment
    requires_reauth = Column(Boolean, default=False)
    
    # Additional data
    session_data = Column(Text, nullable=True)  # JSON string for extra data
    
    # Relationships
    user = relationship("User", back_populates="sessions")
    organization = relationship("Organization")

    def __repr__(self) -> str:
        return f"<UserSession(id={self.id}, session_id={self.session_id}, user_id={self.user_id})>"


class SessionManager:
    """
    Comprehensive session management service.
    """
    
    def __init__(self, db: Session, redis_client: Optional[Redis] = None):
        self.db = db
        self.redis = redis_client
        self.audit_service = AuditService(db)
        
        # Configuration
        self.default_session_timeout = timedelta(hours=8)
        self.api_session_timeout = timedelta(hours=24)
        self.max_concurrent_sessions = 5
        self.session_extension_threshold = timedelta(minutes=30)
        self.trusted_device_timeout = timedelta(days=30)
    
    def create_session(
        self,
        user_id: int,
        request: Request,
        session_type: SessionType = SessionType.WEB,
        organization_id: Optional[int] = None,
        login_method: str = "password",
        is_trusted_device: bool = False,
        custom_timeout: Optional[timedelta] = None
    ) -> SessionInfo:
        """
        Create a new user session.
        
        Args:
            user_id: ID of the user
            request: FastAPI request object
            session_type: Type of session
            organization_id: Organization context
            login_method: How the user authenticated
            is_trusted_device: Whether this is a trusted device
            custom_timeout: Custom session timeout
            
        Returns:
            SessionInfo object with session details
        """
        # Generate unique session ID
        session_id = self._generate_session_id()
        
        # Extract client information
        ip_address = self._get_client_ip(request)
        user_agent = request.headers.get("user-agent", "")
        device_fingerprint = self._generate_device_fingerprint(request)
        
        # Calculate session timeout
        if custom_timeout:
            timeout = custom_timeout
        elif session_type == SessionType.API:
            timeout = self.api_session_timeout
        elif is_trusted_device:
            timeout = self.trusted_device_timeout
        else:
            timeout = self.default_session_timeout
        
        expires_at = datetime.utcnow() + timeout
        
        # Check concurrent session limit
        self._enforce_concurrent_session_limit(user_id)
        
        # Create database session record
        db_session = UserSession(
            session_id=session_id,
            user_id=user_id,
            organization_id=organization_id,
            session_type=session_type,
            ip_address=ip_address,
            user_agent=user_agent,
            device_fingerprint=device_fingerprint,
            is_trusted_device=is_trusted_device,
            expires_at=expires_at,
            login_method=login_method,
            risk_score=self._calculate_risk_score(request, user_id)
        )
        
        self.db.add(db_session)
        self.db.commit()
        self.db.refresh(db_session)
        
        # Store session in Redis for fast lookup
        session_info = SessionInfo(
            session_id=session_id,
            user_id=user_id,
            session_type=session_type,
            ip_address=ip_address,
            user_agent=user_agent,
            created_at=db_session.created_at,
            last_activity=db_session.last_activity,
            expires_at=expires_at,
            status=SessionStatus.ACTIVE,
            organization_id=organization_id,
            device_fingerprint=device_fingerprint,
            is_trusted_device=is_trusted_device,
            concurrent_session_count=self._get_user_session_count(user_id)
        )
        
        self._store_session_in_cache(session_info)
        
        # Audit log
        self.audit_service.log_authentication(
            user_id=user_id,
            action=AuditAction.LOGIN,
            ip_address=ip_address,
            user_agent=user_agent,
            session_id=session_id
        )
        
        logger.info(f"Created session {session_id} for user {user_id}")
        return session_info
    
    def validate_session(
        self,
        session_id: str,
        request: Optional[Request] = None,
        extend_session: bool = True
    ) -> Optional[SessionInfo]:
        """
        Validate and optionally extend a session.
        
        Args:
            session_id: Session ID to validate
            request: Current request (for security checks)
            extend_session: Whether to extend session on activity
            
        Returns:
            SessionInfo if valid, None otherwise
        """
        # Try cache first
        session_info = self._get_session_from_cache(session_id)
        
        if not session_info:
            # Fallback to database
            db_session = self.db.query(UserSession).filter(
                UserSession.session_id == session_id,
                UserSession.status == SessionStatus.ACTIVE
            ).first()
            
            if not db_session:
                return None
            
            session_info = self._db_session_to_info(db_session)
        
        # Check if session is expired
        if datetime.utcnow() > session_info.expires_at:
            self.terminate_session(session_id, SessionStatus.EXPIRED)
            return None
        
        # Security checks
        if request and not self._validate_session_security(session_info, request):
            self.terminate_session(session_id, SessionStatus.LOCKED)
            return None
        
        # Extend session if requested and threshold met
        if extend_session and self._should_extend_session(session_info):
            session_info = self._extend_session(session_info)
        
        # Update last activity
        self._update_last_activity(session_id)
        
        return session_info
    
    def terminate_session(
        self,
        session_id: str,
        status: SessionStatus = SessionStatus.TERMINATED,
        user_id: Optional[int] = None
    ) -> bool:
        """
        Terminate a specific session.
        
        Args:
            session_id: Session ID to terminate
            status: Final status for the session
            user_id: User ID (for audit logging)
            
        Returns:
            True if session was terminated
        """
        # Update database
        db_session = self.db.query(UserSession).filter(
            UserSession.session_id == session_id
        ).first()
        
        if not db_session:
            return False
        
        db_session.status = status
        db_session.terminated_at = datetime.utcnow()
        self.db.commit()
        
        # Remove from cache
        self._remove_session_from_cache(session_id)
        
        # Audit log
        if user_id or db_session.user_id:
            self.audit_service.log_authentication(
                user_id=user_id or db_session.user_id,
                action=AuditAction.LOGOUT,
                ip_address=db_session.ip_address,
                user_agent=db_session.user_agent or "",
                session_id=session_id
            )
        
        logger.info(f"Terminated session {session_id} with status {status}")
        return True
    
    def terminate_user_sessions(
        self,
        user_id: int,
        exclude_session_id: Optional[str] = None,
        reason: str = "user_logout"
    ) -> int:
        """
        Terminate all sessions for a user.
        
        Args:
            user_id: User ID
            exclude_session_id: Session to keep active
            reason: Reason for termination
            
        Returns:
            Number of sessions terminated
        """
        query = self.db.query(UserSession).filter(
            UserSession.user_id == user_id,
            UserSession.status == SessionStatus.ACTIVE
        )
        
        if exclude_session_id:
            query = query.filter(UserSession.session_id != exclude_session_id)
        
        sessions = query.all()
        terminated_count = 0
        
        for session in sessions:
            session.status = SessionStatus.TERMINATED
            session.terminated_at = datetime.utcnow()
            self._remove_session_from_cache(session.session_id)
            terminated_count += 1
        
        self.db.commit()
        
        # Audit log
        if terminated_count > 0:
            self.audit_service.log_event(
                action=AuditAction.LOGOUT,
                description=f"Terminated {terminated_count} sessions: {reason}",
                user_id=user_id,
                additional_data={"terminated_count": terminated_count, "reason": reason}
            )
        
        logger.info(f"Terminated {terminated_count} sessions for user {user_id}")
        return terminated_count
    
    def get_user_sessions(
        self,
        user_id: int,
        active_only: bool = True
    ) -> List[SessionInfo]:
        """Get all sessions for a user."""
        query = self.db.query(UserSession).filter(UserSession.user_id == user_id)
        
        if active_only:
            query = query.filter(UserSession.status == SessionStatus.ACTIVE)
        
        sessions = query.order_by(UserSession.last_activity.desc()).all()
        return [self._db_session_to_info(session) for session in sessions]
    
    def cleanup_expired_sessions(self) -> int:
        """Clean up expired sessions from database and cache."""
        cutoff_time = datetime.utcnow()
        
        expired_sessions = self.db.query(UserSession).filter(
            UserSession.status == SessionStatus.ACTIVE,
            UserSession.expires_at < cutoff_time
        ).all()
        
        for session in expired_sessions:
            session.status = SessionStatus.EXPIRED
            session.terminated_at = cutoff_time
            self._remove_session_from_cache(session.session_id)
        
        self.db.commit()
        
        logger.info(f"Cleaned up {len(expired_sessions)} expired sessions")
        return len(expired_sessions)
    
    def _generate_session_id(self) -> str:
        """Generate a cryptographically secure session ID."""
        random_uuid = str(uuid.uuid4())
        timestamp = str(datetime.utcnow().timestamp())
        return hashlib.sha256(f"{random_uuid}{timestamp}".encode()).hexdigest()
    
    def _get_client_ip(self, request: Request) -> str:
        """Extract client IP address from request."""
        # Check for forwarded headers first
        forwarded_for = request.headers.get("x-forwarded-for")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        
        real_ip = request.headers.get("x-real-ip")
        if real_ip:
            return real_ip
        
        return request.client.host if request.client else "unknown"
    
    def _generate_device_fingerprint(self, request: Request) -> str:
        """Generate a device fingerprint for tracking."""
        user_agent = request.headers.get("user-agent", "")
        accept_language = request.headers.get("accept-language", "")
        accept_encoding = request.headers.get("accept-encoding", "")
        
        fingerprint_data = f"{user_agent}{accept_language}{accept_encoding}"
        return hashlib.md5(fingerprint_data.encode()).hexdigest()
    
    def _calculate_risk_score(self, request: Request, user_id: int) -> int:
        """Calculate risk score for the session (0-100)."""
        risk_score = 0
        
        # Check for unusual IP
        ip_address = self._get_client_ip(request)
        recent_ips = self._get_recent_user_ips(user_id)
        if ip_address not in recent_ips:
            risk_score += 20
        
        # Check for unusual user agent
        user_agent = request.headers.get("user-agent", "")
        if not user_agent or "bot" in user_agent.lower():
            risk_score += 30
        
        # Check for missing security headers
        if not request.headers.get("x-forwarded-for"):
            risk_score += 10
        
        return min(risk_score, 100)
    
    def _enforce_concurrent_session_limit(self, user_id: int):
        """Enforce maximum concurrent sessions per user."""
        active_sessions = self.db.query(UserSession).filter(
            UserSession.user_id == user_id,
            UserSession.status == SessionStatus.ACTIVE
        ).count()
        
        if active_sessions >= self.max_concurrent_sessions:
            # Terminate oldest session
            oldest_session = self.db.query(UserSession).filter(
                UserSession.user_id == user_id,
                UserSession.status == SessionStatus.ACTIVE
            ).order_by(UserSession.last_activity.asc()).first()
            
            if oldest_session:
                self.terminate_session(oldest_session.session_id, SessionStatus.TERMINATED)
    
    def _get_user_session_count(self, user_id: int) -> int:
        """Get current active session count for user."""
        return self.db.query(UserSession).filter(
            UserSession.user_id == user_id,
            UserSession.status == SessionStatus.ACTIVE
        ).count()
    
    def _should_extend_session(self, session_info: SessionInfo) -> bool:
        """Check if session should be extended based on activity."""
        time_until_expiry = session_info.expires_at - datetime.utcnow()
        return time_until_expiry < self.session_extension_threshold
    
    def _extend_session(self, session_info: SessionInfo) -> SessionInfo:
        """Extend session expiration time."""
        if session_info.session_type == SessionType.API:
            extension = self.api_session_timeout
        else:
            extension = self.default_session_timeout
        
        new_expires_at = datetime.utcnow() + extension
        
        # Update database
        self.db.query(UserSession).filter(
            UserSession.session_id == session_info.session_id
        ).update({"expires_at": new_expires_at})
        self.db.commit()
        
        # Update session info
        session_info.expires_at = new_expires_at
        
        # Update cache
        self._store_session_in_cache(session_info)
        
        return session_info
    
    def _validate_session_security(self, session_info: SessionInfo, request: Request) -> bool:
        """Validate session security constraints."""
        # Check IP address consistency (optional, could be too strict)
        current_ip = self._get_client_ip(request)
        if session_info.ip_address != current_ip:
            # Log suspicious activity but don't automatically block
            logger.warning(f"IP change for session {session_info.session_id}: {session_info.ip_address} -> {current_ip}")
        
        # Check device fingerprint (if available)
        current_fingerprint = self._generate_device_fingerprint(request)
        if session_info.device_fingerprint and session_info.device_fingerprint != current_fingerprint:
            logger.warning(f"Device fingerprint change for session {session_info.session_id}")
        
        return True  # For now, log warnings but don't block
    
    def _update_last_activity(self, session_id: str):
        """Update last activity timestamp."""
        # Update database (could be optimized with bulk updates)
        self.db.query(UserSession).filter(
            UserSession.session_id == session_id
        ).update({"last_activity": datetime.utcnow()})
        self.db.commit()
    
    def _get_recent_user_ips(self, user_id: int, days: int = 30) -> Set[str]:
        """Get recent IP addresses for a user."""
        from datetime import timedelta
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        sessions = self.db.query(UserSession.ip_address).filter(
            UserSession.user_id == user_id,
            UserSession.created_at >= cutoff_date
        ).distinct().all()
        
        return {session.ip_address for session in sessions}
    
    def _store_session_in_cache(self, session_info: SessionInfo):
        """Store session in Redis cache."""
        if not self.redis:
            return
        
        try:
            session_data = json.dumps(asdict(session_info), default=str)
            ttl = int((session_info.expires_at - datetime.utcnow()).total_seconds())
            self.redis.setex(f"session:{session_info.session_id}", ttl, session_data)
        except Exception as e:
            logger.error(f"Failed to store session in cache: {e}")
    
    def _get_session_from_cache(self, session_id: str) -> Optional[SessionInfo]:
        """Retrieve session from Redis cache."""
        if not self.redis:
            return None
        
        try:
            session_data = self.redis.get(f"session:{session_id}")
            if session_data:
                data = json.loads(session_data)
                # Convert string dates back to datetime
                data['created_at'] = datetime.fromisoformat(data['created_at'])
                data['last_activity'] = datetime.fromisoformat(data['last_activity'])
                data['expires_at'] = datetime.fromisoformat(data['expires_at'])
                return SessionInfo(**data)
        except Exception as e:
            logger.error(f"Failed to retrieve session from cache: {e}")
        
        return None
    
    def _remove_session_from_cache(self, session_id: str):
        """Remove session from Redis cache."""
        if not self.redis:
            return
        
        try:
            self.redis.delete(f"session:{session_id}")
        except Exception as e:
            logger.error(f"Failed to remove session from cache: {e}")
    
    def _db_session_to_info(self, db_session: UserSession) -> SessionInfo:
        """Convert database session to SessionInfo."""
        return SessionInfo(
            session_id=db_session.session_id,
            user_id=db_session.user_id,
            session_type=SessionType(db_session.session_type),
            ip_address=db_session.ip_address,
            user_agent=db_session.user_agent or "",
            created_at=db_session.created_at,
            last_activity=db_session.last_activity,
            expires_at=db_session.expires_at,
            status=SessionStatus(db_session.status),
            organization_id=db_session.organization_id,
            device_fingerprint=db_session.device_fingerprint,
            is_trusted_device=db_session.is_trusted_device,
            concurrent_session_count=self._get_user_session_count(db_session.user_id)
        )
