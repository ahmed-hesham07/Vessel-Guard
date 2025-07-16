"""
API dependencies for authentication, database, and common functionality.

Provides dependency injection for FastAPI endpoints including
user authentication, database sessions, and permission checks.
"""

from typing import Generator, Optional, Union, List

from jose import jwt
from fastapi import Depends, HTTPException, status, Query
from fastapi.security import OAuth2PasswordBearer
from jose.exceptions import JWTError as InvalidTokenError
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import verify_token
from app.crud.user import user_crud
from app.db.base import get_db
from app.db.models.user import User, UserRole
from app.db.models.organization import Organization

# OAuth2 scheme for token authentication
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/auth/login"
)


def get_current_user(
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme)
) -> User:
    """
    Get current authenticated user from JWT token.
    
    Args:
        db: Database session
        token: JWT access token
        
    Returns:
        Current authenticated user
        
    Raises:
        HTTPException: If token is invalid or user not found
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = verify_token(token, token_type="access")
        if payload is None:
            raise credentials_exception
            
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
            
    except InvalidTokenError:
        raise credentials_exception
    
    user = user_crud.get(db, id=int(user_id))
    if user is None:
        raise credentials_exception
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    
    return user


def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """
    Get current active user.
    
    Args:
        current_user: Current user from token
        
    Returns:
        Active user
        
    Raises:
        HTTPException: If user is inactive
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    return current_user


def get_current_superuser(
    current_user: User = Depends(get_current_user),
) -> User:
    """
    Get current superuser.
    
    Args:
        current_user: Current user from token
        
    Returns:
        Superuser
        
    Raises:
        HTTPException: If user is not a superuser
    """
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    return current_user


def require_role(required_role: Union[UserRole, List[UserRole], str, List[str]]):
    """
    Dependency factory for role-based access control.
    
    Args:
        required_role: Minimum required role(s). Can be a single role or list of roles.
                      Supports both UserRole enum and string values.
        
    Returns:
        Dependency function that checks user role
    """
    def role_checker(current_user: User = Depends(get_current_user)) -> User:
        role_hierarchy = {
            UserRole.VIEWER: 0,
            UserRole.INSPECTOR: 1,
            UserRole.ENGINEER: 2,
            UserRole.MANAGER: 3,
            UserRole.ADMIN: 4
        }
        
        # Convert string roles to UserRole enum
        string_to_role = {
            "viewer": UserRole.VIEWER,
            "inspector": UserRole.INSPECTOR,
            "engineer": UserRole.ENGINEER,
            "manager": UserRole.MANAGER,
            "admin": UserRole.ADMIN,
            "organization_admin": UserRole.ADMIN,
            "super_admin": UserRole.ADMIN
        }
        
        user_level = role_hierarchy.get(current_user.role, 0)
        
        # Handle single role or list of roles
        if isinstance(required_role, list):
            # Check if user has any of the required roles
            allowed = False
            for role in required_role:
                if isinstance(role, str):
                    role_enum = string_to_role.get(role.lower())
                    if role_enum is None:
                        continue
                else:
                    role_enum = role
                
                required_level = role_hierarchy.get(role_enum, 0)
                if user_level >= required_level:
                    allowed = True
                    break
            
            if not allowed and not current_user.is_superuser:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Insufficient permissions. Required one of: {required_role}, Current: {current_user.role}"
                )
        else:
            # Handle single role
            if isinstance(required_role, str):
                role_enum = string_to_role.get(required_role.lower())
                if role_enum is None:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Invalid role: {required_role}"
                    )
            else:
                role_enum = required_role
                
            required_level = role_hierarchy.get(role_enum, 0)
            
            if user_level < required_level and not current_user.is_superuser:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Insufficient permissions. Required: {required_role}, Current: {current_user.role}"
                )
        
        return current_user
    
    return role_checker


def require_admin():
    """Require admin role."""
    return require_role(UserRole.ADMIN)


def require_manager():
    """Require manager role or higher."""
    return require_role(UserRole.MANAGER)


def require_engineer():
    """Require engineer role or higher."""
    return require_role(UserRole.ENGINEER)


def require_inspector():
    """Require inspector role or higher."""
    return require_role(UserRole.INSPECTOR)


def get_current_organization(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Organization:
    """
    Get current user's organization.
    
    Args:
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        User's organization
        
    Raises:
        HTTPException: If organization not found
    """
    if not current_user.organization:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization not found"
        )
    
    return current_user.organization


def check_organization_access(
    organization_id: int,
    current_user: User = Depends(get_current_user)
) -> bool:
    """
    Check if user has access to specified organization.
    
    Args:
        organization_id: Organization ID to check
        current_user: Current authenticated user
        
    Returns:
        True if user has access
        
    Raises:
        HTTPException: If access denied
    """
    if current_user.is_superuser:
        return True
    
    if current_user.organization_id != organization_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to this organization"
        )
    
    return True


def get_optional_user(
    db: Session = Depends(get_db),
    token: Optional[str] = Depends(oauth2_scheme)
) -> Optional[User]:
    """
    Get current user if token is provided and valid, None otherwise.
    
    Args:
        db: Database session
        token: Optional JWT token
        
    Returns:
        User if authenticated, None otherwise
    """
    if not token:
        return None
    
    try:
        payload = verify_token(token, token_type="access")
        if payload is None:
            return None
            
        user_id: str = payload.get("sub")
        if user_id is None:
            return None
            
        user = user_crud.get(db, id=int(user_id))
        if user and user.is_active:
            return user
            
    except (InvalidTokenError, ValueError):
        pass
    
    return None


class Pagination:
    """Pagination parameters dependency."""
    
    def __init__(
        self,
        page: int = 1,
        limit: int = 20,
        sort: str = "created_at",
        order: str = "desc"
    ):
        self.page = max(1, page)
        self.limit = min(100, max(1, limit))  # Max 100 items per page
        self.sort = sort
        self.order = order.lower() if order.lower() in ["asc", "desc"] else "desc"
        
        # Calculate offset
        self.offset = (self.page - 1) * self.limit
    
    @property
    def skip(self) -> int:
        """Get number of items to skip."""
        return self.offset
    
    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "page": self.page,
            "limit": self.limit,
            "sort": self.sort,
            "order": self.order,
            "offset": self.offset
        }


def get_pagination_params(
    skip: int = Query(0, ge=0, description="Number of items to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of items to return")
):
    """
    Get pagination parameters for API endpoints.
    
    Args:
        skip: Number of items to skip (offset)
        limit: Maximum number of items to return
        
    Returns:
        Dictionary with skip and limit values
    """
    return {"skip": skip, "limit": limit}
