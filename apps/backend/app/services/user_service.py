"""
User service layer for handling user-related business logic.

This service provides methods for user creation, authentication,
updates, and organization management.
"""

from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.db.models.user import User, UserRole
from app.db.models.organization import Organization
from app.schemas.user import UserCreate, UserUpdate, UserResponse
from app.core.security import get_password_hash, verify_password
from app.core.exceptions import ValidationError, NotFoundError
from app.utils.validation import validate_email, validate_password


class UserService:
    """Service class for user operations."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_user(self, user_data: UserCreate) -> User:
        """Create a new user."""
        # Validate email format
        if not validate_email(user_data.email):
            raise ValidationError("Invalid email format")
        
        # Validate password strength
        if not validate_password(user_data.password):
            raise ValidationError("Password does not meet security requirements")
        
        # Check if email already exists
        if self.get_user_by_email(user_data.email):
            raise ValidationError("Email already registered")
        
        # Verify organization exists
        organization = self.db.query(Organization).filter(
            Organization.id == user_data.organization_id
        ).first()
        if not organization:
            raise ValidationError("Invalid organization ID")
        
        # Create user
        hashed_password = get_password_hash(user_data.password)
        
        db_user = User(
            email=user_data.email,
            hashed_password=hashed_password,
            first_name=user_data.first_name,
            last_name=user_data.last_name,
            role=user_data.role,
            organization_id=user_data.organization_id,
            is_active=True,
            is_verified=False  # Email verification required
        )
        
        try:
            self.db.add(db_user)
            self.db.commit()
            self.db.refresh(db_user)
            return db_user
        except IntegrityError:
            self.db.rollback()
            raise ValidationError("Email already registered")
    
    def get_user_by_id(self, user_id: int) -> Optional[User]:
        """Get user by ID."""
        return self.db.query(User).filter(User.id == user_id).first()
    
    def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email address."""
        return self.db.query(User).filter(User.email == email).first()
    
    def update_user(self, user_id: int, user_data: UserUpdate) -> User:
        """Update user information."""
        user = self.get_user_by_id(user_id)
        if not user:
            raise NotFoundError("User not found")
        
        # Update fields that are provided
        update_data = user_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            if field == "password":
                # Hash new password
                user.hashed_password = get_password_hash(value)
            else:
                setattr(user, field, value)
        
        try:
            self.db.commit()
            self.db.refresh(user)
            return user
        except IntegrityError:
            self.db.rollback()
            raise ValidationError("Update failed - possibly duplicate email")
    
    def deactivate_user(self, user_id: int) -> User:
        """Deactivate a user account."""
        user = self.get_user_by_id(user_id)
        if not user:
            raise NotFoundError("User not found")
        
        user.is_active = False
        self.db.commit()
        self.db.refresh(user)
        return user
    
    def activate_user(self, user_id: int) -> User:
        """Activate a user account."""
        user = self.get_user_by_id(user_id)
        if not user:
            raise NotFoundError("User not found")
        
        user.is_active = True
        self.db.commit()
        self.db.refresh(user)
        return user
    
    def verify_user_email(self, user_id: int) -> User:
        """Mark user email as verified."""
        user = self.get_user_by_id(user_id)
        if not user:
            raise NotFoundError("User not found")
        
        user.is_verified = True
        self.db.commit()
        self.db.refresh(user)
        return user
    
    def change_password(self, user_id: int, current_password: str, new_password: str) -> bool:
        """Change user password."""
        user = self.get_user_by_id(user_id)
        if not user:
            raise NotFoundError("User not found")
        
        # Verify current password
        if not verify_password(current_password, user.hashed_password):
            raise ValidationError("Current password is incorrect")
        
        # Validate new password
        if not validate_password(new_password):
            raise ValidationError("New password does not meet security requirements")
        
        # Update password
        user.hashed_password = get_password_hash(new_password)
        self.db.commit()
        return True
    
    def get_organization_members(self, organization_id: int, 
                               role: Optional[UserRole] = None,
                               active_only: bool = True) -> List[User]:
        """Get all members of an organization."""
        query = self.db.query(User).filter(User.organization_id == organization_id)
        
        if role:
            query = query.filter(User.role == role)
        
        if active_only:
            query = query.filter(User.is_active == True)
        
        return query.all()
    
    def get_user_permissions(self, user_id: int) -> dict:
        """Get user permissions based on role."""
        user = self.get_user_by_id(user_id)
        if not user:
            raise NotFoundError("User not found")
        
        # Define permissions based on role
        permissions = {
            UserRole.ENGINEER: {
                "can_manage_organizations": False,
                "can_manage_users": False,
                "can_create_projects": True,
                "can_edit_projects": True,
                "can_delete_projects": True,
                "can_perform_calculations": True,
                "can_approve_calculations": True,
                "can_generate_reports": True,
                "can_manage_materials": True,
                "can_view_all_data": True
            },
            UserRole.CONSULTANT: {
                "can_manage_organizations": False,
                "can_manage_users": False,
                "can_create_projects": True,
                "can_edit_projects": True,
                "can_delete_projects": False,
                "can_perform_calculations": True,
                "can_approve_calculations": False,
                "can_generate_reports": True,
                "can_manage_materials": False,
                "can_view_all_data": False
            }
        }
        
        return permissions.get(user.role, {})
    
    def check_permission(self, user_id: int, permission: str) -> bool:
        """Check if user has specific permission."""
        permissions = self.get_user_permissions(user_id)
        return permissions.get(permission, False)
    
    def search_users(self, organization_id: int, 
                    search_term: str = None,
                    role: UserRole = None,
                    active_only: bool = True) -> List[User]:
        """Search users within an organization."""
        query = self.db.query(User).filter(User.organization_id == organization_id)
        
        if search_term:
            search_filter = (
                User.first_name.ilike(f"%{search_term}%") |
                User.last_name.ilike(f"%{search_term}%") |
                User.email.ilike(f"%{search_term}%")
            )
            query = query.filter(search_filter)
        
        if role:
            query = query.filter(User.role == role)
        
        if active_only:
            query = query.filter(User.is_active == True)
        
        return query.all()
    
    def get_user_statistics(self, organization_id: int) -> dict:
        """Get user statistics for an organization."""
        total_users = self.db.query(User).filter(
            User.organization_id == organization_id
        ).count()
        
        active_users = self.db.query(User).filter(
            User.organization_id == organization_id,
            User.is_active == True
        ).count()
        
        # Count users by role
        role_counts = {}
        for role in UserRole:
            count = self.db.query(User).filter(
                User.organization_id == organization_id,
                User.role == role,
                User.is_active == True
            ).count()
            role_counts[role.value] = count
        
        return {
            "total_users": total_users,
            "active_users": active_users,
            "inactive_users": total_users - active_users,
            "role_distribution": role_counts
        }
