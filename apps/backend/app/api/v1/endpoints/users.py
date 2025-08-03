"""
User API endpoints.

Handles user management, profile updates, and
organization member administration.
"""

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.dependencies import (
    get_current_user,
    get_db,
    require_role,
    get_pagination_params
)
from app.crud import user as user_crud
from app.db.models.user import User
from app.schemas import (
    User as UserSchema,
    UserCreate,
    UserUpdate,
    UserList,
    UserSummary,
    UserProfile,
    PasswordReset,
    PasswordChange
)

router = APIRouter()


@router.get("/", response_model=UserList)
def get_users(
    search: Optional[str] = Query(None, min_length=1),
    role: Optional[str] = Query(None),
    active_only: bool = Query(True),
    organization_only: bool = Query(True),
    pagination: dict = Depends(get_pagination_params),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get users.
    
    Organization admins can see users in their organization.
    Super admins can see all users.
    Regular users cannot access this endpoint.
    """
    # Extract pagination parameters
    skip = pagination["skip"]
    limit = pagination["limit"]
    
    if current_user.role not in ["organization_admin", "super_admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to list users"
        )
    
    # Determine organization filter
    organization_id = None
    if current_user.role == "organization_admin" or organization_only:
        organization_id = current_user.organization_id
        if not organization_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User is not associated with any organization"
            )
    
    # Apply filters
    if search:
        users = user_crud.search(
            db, query=search, organization_id=organization_id, skip=skip, limit=limit
        )
        total = len(user_crud.search(db, query=search, organization_id=organization_id, skip=0, limit=10000))
    elif role:
        users = user_crud.get_by_role(
            db, role=role, organization_id=organization_id, skip=skip, limit=limit
        )
        total = len(user_crud.get_by_role(db, role=role, organization_id=organization_id, skip=0, limit=10000))
    elif active_only:
        if organization_id:
            users = user_crud.get_active_by_organization(
                db, organization_id=organization_id, skip=skip, limit=limit
            )
            total = len(user_crud.get_active_by_organization(db, organization_id=organization_id, skip=0, limit=10000))
        else:
            users = user_crud.get_active_users(db, skip=skip, limit=limit)
            total = len(user_crud.get_active_users(db, skip=0, limit=10000))
    else:
        if organization_id:
            users = user_crud.get_by_organization(
                db, organization_id=organization_id, skip=skip, limit=limit
            )
            total = user_crud.get_user_count_by_organization(db, organization_id=organization_id)
        else:
            users = user_crud.get_multi(db, skip=skip, limit=limit)
            total = user_crud.count(db)
    
    return UserList(
        items=users,
        total=total,
        page=skip // limit + 1,
        per_page=limit,
        pages=(total + limit - 1) // limit
    )


@router.post("/", response_model=UserSchema, status_code=status.HTTP_201_CREATED)
def create_user(
    user_in: UserCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["organization_admin", "super_admin"]))
):
    """
    Create new user.
    
    Organization admins can create users in their organization.
    Super admins can create users in any organization.
    """
    # Check if email already exists
    existing_user = user_crud.get_by_email(db, email=user_in.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email already exists"
        )
    
    # Set organization if not specified
    if not user_in.organization_id:
        if current_user.role == "organization_admin":
            user_in.organization_id = current_user.organization_id
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Organization ID is required"
            )
    
    # Check permissions for organization
    if current_user.role == "organization_admin" and user_in.organization_id != current_user.organization_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot create user in different organization"
        )
    
    # Check if organization can add more members
    from app.crud import organization as org_crud
    if not org_crud.can_add_member(db, organization_id=user_in.organization_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Organization has reached its member limit"
        )
    
    # Validate role assignment
    if user_in.role == "super_admin" and current_user.role != "super_admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only super admins can create super admin users"
        )
    
    if user_in.role == "organization_admin" and current_user.role not in ["super_admin", "organization_admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can create organization admin users"
        )
    
    user = user_crud.create(db, obj_in=user_in)
    return user


@router.get("/me", response_model=UserProfile)
def get_current_user_profile(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get current user's profile.
    """
    # Get additional profile information
    login_count = getattr(current_user, 'login_count', 0)
    failed_login_attempts = getattr(current_user, 'failed_login_attempts', 0)
    
    profile_data = {
        **current_user.__dict__,
        "login_count": login_count,
        "failed_login_attempts": failed_login_attempts
    }
    
    return UserProfile(**profile_data)


@router.put("/me", response_model=UserSchema)
def update_current_user_profile(
    user_in: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update current user's profile.
    
    Users can update their own basic information but not role or organization.
    """
    # Remove fields that users cannot update themselves
    update_data = user_in.dict(exclude_unset=True)
    restricted_fields = ["role", "organization_id", "is_active", "is_verified"]
    
    for field in restricted_fields:
        if field in update_data:
            del update_data[field]
    
    user = user_crud.update(db, db_obj=current_user, obj_in=update_data)
    return user


@router.post("/me/change-password", response_model=dict)
def change_password(
    password_data: PasswordChange,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Change current user's password.
    """
    # Verify current password
    if not user_crud.authenticate(db, email=current_user.email, password=password_data.current_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect"
        )
    
    # Update password
    user_crud.update_password(db, user_id=current_user.id, new_password=password_data.new_password)
    
    return {"message": "Password updated successfully"}


@router.get("/{user_id}", response_model=UserSchema)
def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get user by ID.
    
    Users can only access their own profile unless they are admin.
    """
    user = user_crud.get(db, id=user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Check permissions
    if (current_user.id != user_id and 
        current_user.role not in ["organization_admin", "super_admin"]):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to access this user"
        )
    
    # Organization admins can only access users in their organization
    if (current_user.role == "organization_admin" and 
        user.organization_id != current_user.organization_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot access user from different organization"
        )
    
    return user


@router.put("/{user_id}", response_model=UserSchema)
def update_user(
    user_id: int,
    user_in: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["organization_admin", "super_admin"]))
):
    """
    Update user.
    
    Organization admins can update users in their organization.
    Super admins can update any user.
    """
    user = user_crud.get(db, id=user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Check permissions
    if (current_user.role == "organization_admin" and 
        user.organization_id != current_user.organization_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot update user from different organization"
        )
    
    # Validate role changes
    update_data = user_in.dict(exclude_unset=True)
    
    if "role" in update_data:
        new_role = update_data["role"]
        
        # Only super admins can create/modify super admins
        if new_role == "super_admin" and current_user.role != "super_admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only super admins can assign super admin role"
            )
        
        # Only admins can assign organization admin role
        if new_role == "organization_admin" and current_user.role not in ["super_admin", "organization_admin"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only admins can assign organization admin role"
            )
    
    # Validate organization changes
    if "organization_id" in update_data and current_user.role != "super_admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only super admins can change user organization"
        )
    
    user = user_crud.update(db, db_obj=user, obj_in=update_data)
    return user


@router.post("/{user_id}/deactivate", response_model=UserSchema)
def deactivate_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["organization_admin", "super_admin"]))
):
    """
    Deactivate user.
    """
    user = user_crud.get(db, id=user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Check permissions
    if (current_user.role == "organization_admin" and 
        user.organization_id != current_user.organization_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot deactivate user from different organization"
        )
    
    # Cannot deactivate yourself
    if user_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot deactivate yourself"
        )
    
    user = user_crud.update(db, db_obj=user, obj_in={"is_active": False})
    return user


@router.post("/{user_id}/reactivate", response_model=UserSchema)
def reactivate_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["organization_admin", "super_admin"]))
):
    """
    Reactivate user.
    """
    user = user_crud.get(db, id=user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Check permissions
    if (current_user.role == "organization_admin" and 
        user.organization_id != current_user.organization_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot reactivate user from different organization"
        )
    
    user = user_crud.update(db, db_obj=user, obj_in={"is_active": True})
    return user


@router.post("/{user_id}/reset-password", response_model=dict)
def reset_user_password(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["organization_admin", "super_admin"]))
):
    """
    Reset user password (Admin only).
    
    Generates a temporary password that user must change on first login.
    """
    user = user_crud.get(db, id=user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Check permissions
    if (current_user.role == "organization_admin" and 
        user.organization_id != current_user.organization_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot reset password for user from different organization"
        )
    
    # Generate temporary password
    import secrets
    import string
    
    alphabet = string.ascii_letters + string.digits
    temp_password = ''.join(secrets.choice(alphabet) for _ in range(12))
    
    # Update user password and force password change
    user_crud.update_password(db, user_id=user_id, new_password=temp_password)
    user_crud.update(db, db_obj=user, obj_in={"must_change_password": True})
    
    return {
        "message": "Password reset successfully",
        "temporary_password": temp_password,
        "note": "User must change password on next login"
    }


@router.get("/roles/available", response_model=List[str])
def get_available_roles(
    current_user: User = Depends(get_current_user)
):
    """
    Get available roles that current user can assign.
    """
    return ["engineer", "consultant"]
