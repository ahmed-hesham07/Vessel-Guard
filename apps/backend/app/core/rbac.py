"""
Role-Based Access Control (RBAC) system for Vessel Guard.

Provides comprehensive permission management with role hierarchies,
resource-based permissions, and security decorators.
"""

import enum
from typing import Dict, List, Set, Optional
from functools import wraps
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.db.models.user import User, UserRole
from app.core.logging_config import get_logger

logger = get_logger(__name__)


class Permission(str, enum.Enum):
    """System permissions for fine-grained access control."""
    
    # User management
    USER_CREATE = "user:create"
    USER_READ = "user:read"
    USER_UPDATE = "user:update"
    USER_DELETE = "user:delete"
    USER_LIST = "user:list"
    
    # Organization management
    ORG_CREATE = "organization:create"
    ORG_READ = "organization:read"
    ORG_UPDATE = "organization:update"
    ORG_DELETE = "organization:delete"
    ORG_MANAGE_USERS = "organization:manage_users"
    
    # Project management
    PROJECT_CREATE = "project:create"
    PROJECT_READ = "project:read"
    PROJECT_UPDATE = "project:update"
    PROJECT_DELETE = "project:delete"
    PROJECT_LIST = "project:list"
    PROJECT_ASSIGN = "project:assign"
    
    # Vessel management
    VESSEL_CREATE = "vessel:create"
    VESSEL_READ = "vessel:read"
    VESSEL_UPDATE = "vessel:update"
    VESSEL_DELETE = "vessel:delete"
    VESSEL_LIST = "vessel:list"
    
    # Calculation management
    CALC_CREATE = "calculation:create"
    CALC_READ = "calculation:read"
    CALC_UPDATE = "calculation:update"
    CALC_DELETE = "calculation:delete"
    CALC_LIST = "calculation:list"
    CALC_EXECUTE = "calculation:execute"
    CALC_APPROVE = "calculation:approve"
    
    # Inspection management
    INSPECTION_CREATE = "inspection:create"
    INSPECTION_READ = "inspection:read"
    INSPECTION_UPDATE = "inspection:update"
    INSPECTION_DELETE = "inspection:delete"
    INSPECTION_LIST = "inspection:list"
    INSPECTION_SCHEDULE = "inspection:schedule"
    INSPECTION_APPROVE = "inspection:approve"
    
    # Report management
    REPORT_CREATE = "report:create"
    REPORT_READ = "report:read"
    REPORT_UPDATE = "report:update"
    REPORT_DELETE = "report:delete"
    REPORT_LIST = "report:list"
    REPORT_GENERATE = "report:generate"
    REPORT_EXPORT = "report:export"
    
    # Material management
    MATERIAL_CREATE = "material:create"
    MATERIAL_READ = "material:read"
    MATERIAL_UPDATE = "material:update"
    MATERIAL_DELETE = "material:delete"
    MATERIAL_LIST = "material:list"
    
    # System administration
    SYSTEM_ADMIN = "system:admin"
    SYSTEM_BACKUP = "system:backup"
    SYSTEM_MONITOR = "system:monitor"
    SYSTEM_CONFIG = "system:config"
    
    # Audit and compliance
    AUDIT_READ = "audit:read"
    AUDIT_EXPORT = "audit:export"
    COMPLIANCE_READ = "compliance:read"
    COMPLIANCE_MANAGE = "compliance:manage"


class RolePermissions:
    """Role-based permission mapping with inheritance hierarchy."""
    
    # Permission sets for each role
    ROLE_PERMISSIONS: Dict[UserRole, Set[Permission]] = {
        UserRole.ENGINEER: {
            # Full access to all core features
            Permission.PROJECT_READ,
            Permission.PROJECT_CREATE,
            Permission.PROJECT_UPDATE,
            Permission.PROJECT_LIST,
            Permission.VESSEL_READ,
            Permission.VESSEL_CREATE,
            Permission.VESSEL_UPDATE,
            Permission.VESSEL_LIST,
            Permission.CALC_READ,
            Permission.CALC_CREATE,
            Permission.CALC_UPDATE,
            Permission.CALC_DELETE,
            Permission.CALC_LIST,
            Permission.CALC_EXECUTE,
            Permission.INSPECTION_READ,
            Permission.INSPECTION_CREATE,
            Permission.INSPECTION_UPDATE,
            Permission.INSPECTION_LIST,
            Permission.INSPECTION_SCHEDULE,
            Permission.REPORT_READ,
            Permission.REPORT_CREATE,
            Permission.REPORT_UPDATE,
            Permission.REPORT_LIST,
            Permission.REPORT_GENERATE,
            Permission.REPORT_EXPORT,
            Permission.MATERIAL_READ,
            Permission.MATERIAL_CREATE,
            Permission.MATERIAL_UPDATE,
            Permission.USER_READ,
            Permission.USER_UPDATE,  # Can update own profile
        },
        
        UserRole.CONSULTANT: {
            # Read access to most features, limited write access
            Permission.PROJECT_READ,
            Permission.PROJECT_CREATE,
            Permission.PROJECT_UPDATE,
            Permission.PROJECT_LIST,
            Permission.VESSEL_READ,
            Permission.VESSEL_CREATE,
            Permission.VESSEL_UPDATE,
            Permission.VESSEL_LIST,
            Permission.CALC_READ,
            Permission.CALC_CREATE,
            Permission.CALC_UPDATE,
            Permission.CALC_LIST,
            Permission.CALC_EXECUTE,
            Permission.INSPECTION_READ,
            Permission.INSPECTION_CREATE,
            Permission.INSPECTION_UPDATE,
            Permission.INSPECTION_LIST,
            Permission.INSPECTION_SCHEDULE,
            Permission.REPORT_READ,
            Permission.REPORT_CREATE,
            Permission.REPORT_UPDATE,
            Permission.REPORT_LIST,
            Permission.REPORT_GENERATE,
            Permission.REPORT_EXPORT,
            Permission.MATERIAL_READ,
            Permission.MATERIAL_CREATE,
            Permission.MATERIAL_UPDATE,
            Permission.USER_READ,
            Permission.USER_UPDATE,  # Can update own profile
        }
    }

    @classmethod
    def get_permissions(cls, role: UserRole) -> Set[Permission]:
        """Get all permissions for a given role."""
        return cls.ROLE_PERMISSIONS.get(role, set())

    @classmethod
    def has_permission(cls, role: UserRole, permission: Permission) -> bool:
        """Check if a role has a specific permission."""
        return permission in cls.get_permissions(role)

    @classmethod
    def can_access_resource(cls, role: UserRole, resource: str, action: str) -> bool:
        """Check if a role can perform an action on a resource."""
        permission = Permission(f"{resource}:{action}")
        return cls.has_permission(role, permission)


class RBACService:
    """Service class for role-based access control operations."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def check_permission(self, user: User, permission: Permission) -> bool:
        """Check if user has specific permission."""
        if not user.is_active:
            return False
        
        if user.is_superuser:
            return True
        
        return RolePermissions.has_permission(user.role, permission)
    
    def check_resource_access(self, user: User, resource: str, action: str) -> bool:
        """Check if user can perform action on resource."""
        if not user.is_active:
            return False
        
        if user.is_superuser:
            return True
        
        return RolePermissions.can_access_resource(user.role, resource, action)
    
    def check_organization_access(self, user: User, target_org_id: int) -> bool:
        """Check if user can access resources in target organization."""
        if not user.is_active:
            return False
        
        if user.is_superuser:
            return True
        
        # Users can only access resources in their own organization
        return user.organization_id == target_org_id
    
    def check_project_access(self, user: User, project_id: int) -> bool:
        """Check if user can access specific project."""
        # This would typically check project membership or ownership
        # For now, implementing basic organization-based access
        return self.check_organization_access(user, user.organization_id)
    
    def get_user_permissions(self, user: User) -> Set[Permission]:
        """Get all permissions for a user."""
        if not user.is_active:
            return set()
        
        if user.is_superuser:
            return set(Permission)
        
        return RolePermissions.get_permissions(user.role)
    
    def can_manage_user(self, current_user: User, target_user: User) -> bool:
        """Check if current user can manage target user."""
        if not current_user.is_active:
            return False
        
        if current_user.is_superuser:
            return True
        
        # Engineers can manage users in their organization
        if current_user.role == UserRole.ENGINEER:
            return current_user.organization_id == target_user.organization_id
        
        # Users can only manage themselves
        return current_user.id == target_user.id


def require_permission(permission: Permission):
    """Decorator to require specific permission for endpoint access."""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Extract current user from dependencies
            current_user = None
            for key, value in kwargs.items():
                if isinstance(value, User):
                    current_user = value
                    break
            
            if not current_user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Authentication required"
                )
            
            # Get database session
            db = None
            for key, value in kwargs.items():
                if hasattr(value, 'query'):  # Check if it's a SQLAlchemy session
                    db = value
                    break
            
            if not db:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Database session not available"
                )
            
            rbac = RBACService(db)
            if not rbac.check_permission(current_user, permission):
                logger.warning(
                    f"Permission denied: User {current_user.id} "
                    f"attempted to access {permission.value}"
                )
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Insufficient permissions: {permission.value} required"
                )
            
            return await func(*args, **kwargs)
        return wrapper
    return decorator


def require_role(min_role: UserRole):
    """Decorator to require minimum role for endpoint access."""
    # Define role hierarchy
    role_hierarchy = {
        UserRole.CONSULTANT: 1,
        UserRole.ENGINEER: 2
    }
    
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Extract current user from dependencies
            current_user = None
            for key, value in kwargs.items():
                if isinstance(value, User):
                    current_user = value
                    break
            
            if not current_user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Authentication required"
                )
            
            if not current_user.is_active:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Account is inactive"
                )
            
            if current_user.is_superuser:
                return await func(*args, **kwargs)
            
            user_level = role_hierarchy.get(current_user.role, -1)
            required_level = role_hierarchy.get(min_role, 99)
            
            if user_level < required_level:
                logger.warning(
                    f"Role check failed: User {current_user.id} "
                    f"with role {current_user.role} attempted to access "
                    f"endpoint requiring {min_role}"
                )
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Insufficient role: {min_role.value} or higher required"
                )
            
            return await func(*args, **kwargs)
        return wrapper
    return decorator


def require_organization_access(org_id_param: str = "organization_id"):
    """Decorator to require access to specific organization."""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Extract current user and organization ID
            current_user = None
            org_id = None
            
            for key, value in kwargs.items():
                if isinstance(value, User):
                    current_user = value
                elif key == org_id_param:
                    org_id = value
            
            if not current_user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Authentication required"
                )
            
            if org_id is None:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Organization ID required"
                )
            
            # Get database session
            db = None
            for key, value in kwargs.items():
                if hasattr(value, 'query'):
                    db = value
                    break
            
            if not db:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Database session not available"
                )
            
            rbac = RBACService(db)
            if not rbac.check_organization_access(current_user, org_id):
                logger.warning(
                    f"Organization access denied: User {current_user.id} "
                    f"attempted to access organization {org_id}"
                )
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Access to this organization is not allowed"
                )
            
            return await func(*args, **kwargs)
        return wrapper
    return decorator
