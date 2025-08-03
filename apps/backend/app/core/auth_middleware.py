"""
Enhanced authentication and authorization middleware.

Integrates RBAC, session management, audit logging,
and data protection features.
"""

import uuid
from datetime import datetime
from typing import Optional, List, Dict, Any
from fastapi import Request, HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
import jwt
import jwt
from jwt.exceptions import JWTException, JWTDecodeError

from app.core.config import settings
from app.core.rbac import RBACService, Permission
from app.core.session_manager import SessionManager, SessionType, SessionStatus
from app.core.audit import AuditService, AuditAction, AuditSeverity
from app.core.data_protection import encryption_manager
from app.api.dependencies import get_db
from app.db.models.user import User, UserRole
from app.core.logging_config import get_logger

logger = get_logger(__name__)

# Security scheme
security = HTTPBearer(auto_error=False)


class AuthContext:
    """Authentication context for the current request."""
    
    def __init__(
        self,
        user: User,
        session_id: str,
        permissions: List[Permission],
        organization_id: int,
        is_admin: bool = False,
        request_id: str = None
    ):
        self.user = user
        self.session_id = session_id
        self.permissions = permissions
        self.organization_id = organization_id
        self.is_admin = is_admin
        self.request_id = request_id or str(uuid.uuid4())
    
    def has_permission(self, permission: Permission) -> bool:
        """Check if user has specific permission."""
        return permission in self.permissions or self.is_admin
    
    def has_any_permission(self, permissions: List[Permission]) -> bool:
        """Check if user has any of the specified permissions."""
        return any(self.has_permission(p) for p in permissions) or self.is_admin
    
    def has_all_permissions(self, permissions: List[Permission]) -> bool:
        """Check if user has all of the specified permissions."""
        return all(self.has_permission(p) for p in permissions) or self.is_admin


class AuthenticationService:
    """
    Enhanced authentication service with RBAC and session management.
    """
    
    def __init__(self, db: Session):
        self.db = db
        self.rbac_service = RBACService(db)
        self.session_manager = SessionManager(db)
        self.audit_service = AuditService(db)
    
    def authenticate_token(
        self,
        token: str,
        request: Request
    ) -> Optional[AuthContext]:
        """
        Authenticate JWT token and create auth context.
        
        Args:
            token: JWT token
            request: FastAPI request
            
        Returns:
            AuthContext if valid, None otherwise
        """
        try:
            # Decode JWT token
            payload = jwt.decode(
                token,
                settings.SECRET_KEY,
                algorithms=[settings.ALGORITHM]
            )
            
            user_id: int = payload.get("sub")
            session_id: str = payload.get("session_id")
            
            if user_id is None or session_id is None:
                return None
            
            # Get user from database
            user = self.db.query(User).filter(User.id == user_id).first()
            if not user or not user.is_active:
                return None
            
            # Validate session
            session_info = self.session_manager.validate_session(
                session_id=session_id,
                request=request,
                extend_session=True
            )
            
            if not session_info:
                return None
            
            # Get user permissions
            permissions = self.rbac_service.get_user_permissions(user)
            
            # Create auth context
            auth_context = AuthContext(
                user=user,
                session_id=session_id,
                permissions=permissions,
                organization_id=user.organization_id,
                is_admin=user.is_admin
            )
            
            return auth_context
            
        except JWTException as e:
            logger.warning(f"JWT decode error: {e}")
            return None
        except Exception as e:
            logger.error(f"Authentication error: {e}")
            return None
    
    def create_access_token(
        self,
        user: User,
        session_id: str,
        expires_delta: Optional[int] = None
    ) -> str:
        """Create JWT access token."""
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + settings.ACCESS_TOKEN_EXPIRE_MINUTES
        
        to_encode = {
            "sub": user.id,
            "email": user.email,
            "role": user.role.value,
            "organization_id": user.organization_id,
            "session_id": session_id,
            "exp": expire,
            "iat": datetime.utcnow(),
            "type": "access"
        }
        
        encoded_jwt = jwt.encode(
            to_encode,
            settings.SECRET_KEY,
            algorithm=settings.ALGORITHM
        )
        
        return encoded_jwt
    
    def create_refresh_token(
        self,
        user: User,
        session_id: str
    ) -> str:
        """Create JWT refresh token."""
        expire = datetime.utcnow() + settings.REFRESH_TOKEN_EXPIRE_DAYS
        
        to_encode = {
            "sub": user.id,
            "session_id": session_id,
            "exp": expire,
            "iat": datetime.utcnow(),
            "type": "refresh"
        }
        
        encoded_jwt = jwt.encode(
            to_encode,
            settings.SECRET_KEY,
            algorithm=settings.ALGORITHM
        )
        
        return encoded_jwt
    
    def refresh_access_token(
        self,
        refresh_token: str,
        request: Request
    ) -> Optional[Dict[str, str]]:
        """
        Refresh access token using refresh token.
        
        Args:
            refresh_token: JWT refresh token
            request: FastAPI request
            
        Returns:
            New token pair or None if invalid
        """
        try:
            # Decode refresh token
            payload = jwt.decode(
                refresh_token,
                settings.SECRET_KEY,
                algorithms=[settings.ALGORITHM]
            )
            
            if payload.get("type") != "refresh":
                return None
            
            user_id: int = payload.get("sub")
            session_id: str = payload.get("session_id")
            
            if user_id is None or session_id is None:
                return None
            
            # Validate user and session
            user = self.db.query(User).filter(User.id == user_id).first()
            if not user or not user.is_active:
                return None
            
            session_info = self.session_manager.validate_session(session_id, request)
            if not session_info:
                return None
            
            # Create new token pair
            new_access_token = self.create_access_token(user, session_id)
            new_refresh_token = self.create_refresh_token(user, session_id)
            
            # Audit log
            self.audit_service.log_event(
                action=AuditAction.LOGIN,
                description="Token refreshed",
                user_id=user.id,
                session_id=session_id,
                ip_address=self.session_manager._get_client_ip(request),
                success=True
            )
            
            return {
                "access_token": new_access_token,
                "refresh_token": new_refresh_token,
                "token_type": "bearer"
            }
            
        except JWTException as e:
            logger.warning(f"Refresh token decode error: {e}")
            return None
        except Exception as e:
            logger.error(f"Token refresh error: {e}")
            return None


# Dependency functions
async def get_current_user(
    request: Request,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: Session = Depends(get_db)
) -> AuthContext:
    """
    Get current authenticated user with full context.
    
    Raises HTTPException if not authenticated.
    """
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization header missing",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    auth_service = AuthenticationService(db)
    auth_context = auth_service.authenticate_token(credentials.credentials, request)
    
    if not auth_context:
        # Log failed authentication attempt
        audit_service = AuditService(db)
        audit_service.log_authentication(
            user_id=None,
            action=AuditAction.LOGIN_FAILED,
            ip_address=auth_service.session_manager._get_client_ip(request),
            user_agent=request.headers.get("user-agent", ""),
            success=False,
            error_message="Invalid or expired token"
        )
        
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Store auth context in request state for middleware access
    request.state.auth_context = auth_context
    
    return auth_context


async def get_current_active_user(
    current_user: AuthContext = Depends(get_current_user)
) -> AuthContext:
    """Get current active user (alias for compatibility)."""
    return current_user


def require_permission(permission: Permission):
    """
    Dependency factory for permission-based access control.
    
    Usage:
        @app.get("/admin")
        async def admin_endpoint(
            user: AuthContext = Depends(require_permission(Permission.ADMIN_ACCESS))
        ):
            ...
    """
    def permission_checker(current_user: AuthContext = Depends(get_current_user)) -> AuthContext:
        if not current_user.has_permission(permission):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Insufficient permissions. Required: {permission.value}"
            )
        return current_user
    
    return permission_checker


def require_role(role: UserRole):
    """
    Dependency factory for role-based access control.
    
    Usage:
        @app.get("/manager")
        async def manager_endpoint(
            user: AuthContext = Depends(require_role(UserRole.ENGINEER))
        ):
            ...
    """
    def role_checker(current_user: AuthContext = Depends(get_current_user)) -> AuthContext:
        user_role_hierarchy = {
            UserRole.CONSULTANT: 1,
            UserRole.ENGINEER: 2
        }
        
        required_level = user_role_hierarchy.get(role, 0)
        user_level = user_role_hierarchy.get(current_user.user.role, 0)
        
        if user_level < required_level and not current_user.is_admin:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Insufficient role. Required: {role.value} or higher"
            )
        
        return current_user
    
    return role_checker


def require_organization_access(allow_admin_override: bool = True):
    """
    Dependency factory for organization-based access control.
    
    Ensures user can only access resources from their organization.
    """
    def organization_checker(
        organization_id: int,
        current_user: AuthContext = Depends(get_current_user)
    ) -> AuthContext:
        if (current_user.organization_id != organization_id and 
            not (allow_admin_override and current_user.is_admin)):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied. Resource belongs to different organization"
            )
        
        return current_user
    
    return organization_checker


class AuthenticationMiddleware:
    """
    Middleware for request-level authentication and audit logging.
    """
    
    def __init__(self):
        self.excluded_paths = {
            "/",
            "/health",
            "/api/v1/health", 
            "/docs",
            "/redoc",
            "/openapi.json",
            "/api/v1/auth/login",
            "/api/v1/auth/register",
            "/api/v1/auth/refresh"
        }
    
    async def __call__(self, request: Request, call_next):
        """Process request with authentication and audit logging."""
        start_time = datetime.utcnow()
        request_id = str(uuid.uuid4())
        
        # Skip authentication for excluded paths
        if request.url.path in self.excluded_paths:
            response = await call_next(request)
            return response
        
        # Initialize request state
        request.state.request_id = request_id
        request.state.start_time = start_time
        
        try:
            # Process request
            response = await call_next(request)
            
            # Log successful request
            if hasattr(request.state, 'auth_context'):
                auth_context = request.state.auth_context
                duration_ms = int((datetime.utcnow() - start_time).total_seconds() * 1000)
                
                # Audit log for authenticated requests
                db = next(get_db())
                audit_service = AuditService(db)
                
                audit_service.log_event(
                    action=AuditAction.READ if request.method == "GET" else AuditAction.UPDATE,
                    description=f"{request.method} {request.url.path}",
                    user_id=auth_context.user.id,
                    session_id=auth_context.session_id,
                    ip_address=request.client.host if request.client else "unknown",
                    user_agent=request.headers.get("user-agent", ""),
                    request_id=request_id,
                    endpoint=request.url.path,
                    method=request.method,
                    success=True,
                    duration_ms=duration_ms
                )
            
            return response
            
        except Exception as e:
            # Log failed request
            duration_ms = int((datetime.utcnow() - start_time).total_seconds() * 1000)
            
            try:
                db = next(get_db())
                audit_service = AuditService(db)
                
                user_id = None
                session_id = None
                if hasattr(request.state, 'auth_context'):
                    auth_context = request.state.auth_context
                    user_id = auth_context.user.id
                    session_id = auth_context.session_id
                
                audit_service.log_event(
                    action=AuditAction.READ if request.method == "GET" else AuditAction.UPDATE,
                    description=f"{request.method} {request.url.path}",
                    user_id=user_id,
                    session_id=session_id,
                    ip_address=request.client.host if request.client else "unknown",
                    user_agent=request.headers.get("user-agent", ""),
                    request_id=request_id,
                    endpoint=request.url.path,
                    method=request.method,
                    success=False,
                    error_message=str(e),
                    duration_ms=duration_ms,
                    severity=AuditSeverity.HIGH
                )
            except Exception as audit_error:
                logger.error(f"Failed to log audit event: {audit_error}")
            
            raise e
