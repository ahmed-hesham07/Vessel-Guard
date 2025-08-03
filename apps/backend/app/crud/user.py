"""
CRUD operations for User model.

Provides database operations for user management including
authentication, profile updates, and user administration.
"""

from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

from app.core.security import get_password_hash, verify_password
from app.crud.base import CRUDBase
from app.db.models.user import User, UserRole
from app.schemas.user import UserCreate, UserUpdate


class CRUDUser(CRUDBase[User, UserCreate, UserUpdate]):
    """CRUD operations for User model."""

    def get_by_email(self, db: Session, *, email: str) -> Optional[User]:
        """
        Get user by email address.
        
        Args:
            db: Database session
            email: User email address
            
        Returns:
            User if found, None otherwise
        """
        return db.query(User).filter(User.email == email).first()

    def create(self, db: Session, *, obj_in: UserCreate) -> User:
        """
        Create new user.
        
        Args:
            db: Database session
            obj_in: User creation data
            
        Returns:
            Created user
        """
        hashed_password = get_password_hash(obj_in.password)
        
        db_obj = User(
            email=obj_in.email,
            hashed_password=hashed_password,
            first_name=obj_in.first_name,
            last_name=obj_in.last_name,
            phone=obj_in.phone,
            job_title=obj_in.job_title,
            department=obj_in.department,
            role=obj_in.role,
            timezone=obj_in.timezone,
            language=obj_in.language,
            organization_id=obj_in.organization_id,
            is_active=True,
            is_verified=False  # Require email verification
        )
        
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def authenticate(self, db: Session, *, email: str, password: str) -> Optional[User]:
        """
        Authenticate user with email and password.
        
        Args:
            db: Database session
            email: User email
            password: User password
            
        Returns:
            User if authenticated, None otherwise
        """
        user = self.get_by_email(db, email=email)
        if not user:
            return None
        
        # Check if account is locked before attempting password verification
        if self.is_locked(user):
            return None
        
        if not verify_password(password, user.hashed_password):
            # Increment failed login attempts
            self.increment_failed_login_attempts(db, user=user)
            return None
        
        # Reset failed login attempts on successful login
        self.reset_failed_login_attempts(db, user=user)
        return user

    def update_password(self, db: Session, *, user: User, hashed_password: str) -> User:
        """
        Update user password.
        
        Args:
            db: Database session
            user: User to update
            hashed_password: New hashed password
            
        Returns:
            Updated user
        """
        user.hashed_password = hashed_password
        user.updated_at = datetime.utcnow()
        db.add(user)
        db.commit()
        db.refresh(user)
        return user

    def update_last_login(self, db: Session, *, user: User) -> User:
        """
        Update user's last login timestamp.
        
        Args:
            db: Database session
            user: User to update
            
        Returns:
            Updated user
        """
        user.last_login = datetime.utcnow()
        db.add(user)
        db.commit()
        db.refresh(user)
        return user

    def increment_failed_login_attempts(self, db: Session, *, user: User) -> User:
        """
        Increment failed login attempts counter.
        
        Args:
            db: Database session
            user: User to update
            
        Returns:
            Updated user
        """
        user.failed_login_attempts += 1
        
        # Lock account after 5 failed attempts for 15 minutes
        if user.failed_login_attempts >= 5:
            user.locked_until = datetime.utcnow() + timedelta(minutes=15)
        
        db.add(user)
        db.commit()
        db.refresh(user)
        return user

    def reset_failed_login_attempts(self, db: Session, *, user: User) -> User:
        """
        Reset failed login attempts counter.
        
        Args:
            db: Database session
            user: User to update
            
        Returns:
            Updated user
        """
        user.failed_login_attempts = 0
        user.locked_until = None
        db.add(user)
        db.commit()
        db.refresh(user)
        return user

    def set_password_reset_token(self, db: Session, *, user: User, token: str) -> User:
        """
        Set password reset token.
        
        Args:
            db: Database session
            user: User to update
            token: Reset token
            
        Returns:
            Updated user
        """
        user.password_reset_token = token
        user.password_reset_expires = datetime.utcnow() + timedelta(hours=24)
        db.add(user)
        db.commit()
        db.refresh(user)
        return user

    def clear_password_reset_token(self, db: Session, *, user: User) -> User:
        """
        Clear password reset token.
        
        Args:
            db: Database session
            user: User to update
            
        Returns:
            Updated user
        """
        user.password_reset_token = None
        user.password_reset_expires = None
        db.add(user)
        db.commit()
        db.refresh(user)
        return user

    def verify_email(self, db: Session, *, user: User) -> User:
        """
        Mark user email as verified.
        
        Args:
            db: Database session
            user: User to update
            
        Returns:
            Updated user
        """
        user.is_verified = True
        user.email_verification_token = None
        user.email_verification_expires = None
        db.add(user)
        db.commit()
        db.refresh(user)
        return user

    def deactivate(self, db: Session, *, user: User) -> User:
        """
        Deactivate user account.
        
        Args:
            db: Database session
            user: User to deactivate
            
        Returns:
            Updated user
        """
        user.is_active = False
        db.add(user)
        db.commit()
        db.refresh(user)
        return user

    def activate(self, db: Session, *, user: User) -> User:
        """
        Activate user account.
        
        Args:
            db: Database session
            user: User to activate
            
        Returns:
            Updated user
        """
        user.is_active = True
        db.add(user)
        db.commit()
        db.refresh(user)
        return user

    def get_by_organization(
        self, 
        db: Session, 
        *, 
        organization_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> List[User]:
        """
        Get users by organization.
        
        Args:
            db: Database session
            organization_id: Organization ID
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of users
        """
        return (
            db.query(User)
            .filter(User.organization_id == organization_id)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_by_role(
        self, 
        db: Session, 
        *, 
        role: UserRole,
        organization_id: Optional[int] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[User]:
        """
        Get users by role.
        
        Args:
            db: Database session
            role: User role
            organization_id: Optional organization filter
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of users
        """
        query = db.query(User).filter(User.role == role)
        
        if organization_id:
            query = query.filter(User.organization_id == organization_id)
        
        return query.offset(skip).limit(limit).all()

    def search(
        self,
        db: Session,
        *,
        query: str,
        organization_id: Optional[int] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[User]:
        """
        Search users by name or email.
        
        Args:
            db: Database session
            query: Search query
            organization_id: Optional organization filter
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of matching users
        """
        search_filter = or_(
            User.first_name.ilike(f"%{query}%"),
            User.last_name.ilike(f"%{query}%"),
            User.email.ilike(f"%{query}%")
        )
        
        db_query = db.query(User).filter(search_filter)
        
        if organization_id:
            db_query = db_query.filter(User.organization_id == organization_id)
        
        return db_query.offset(skip).limit(limit).all()

    def count_by_organization(self, db: Session, *, organization_id: int) -> int:
        """
        Count users in organization.
        
        Args:
            db: Database session
            organization_id: Organization ID
            
        Returns:
            Number of users
        """
        return db.query(User).filter(User.organization_id == organization_id).count()

    def is_superuser(self, user: User) -> bool:
        """
        Check if user is superuser.
        
        Args:
            user: User to check
            
        Returns:
            True if superuser
        """
        return user.is_superuser

    def is_active(self, user: User) -> bool:
        """
        Check if user is active.
        
        Args:
            user: User to check
            
        Returns:
            True if active
        """
        return user.is_active and not self.is_locked(user)

    def is_locked(self, user: User) -> bool:
        """
        Check if user account is locked.
        
        Args:
            user: User to check
            
        Returns:
            True if locked
        """
        if not user.locked_until:
            return False
        
        return datetime.utcnow() < user.locked_until


# Create global instance
user_crud = CRUDUser(User)
