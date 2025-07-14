"""
CRUD operations for Organization model.

Handles organization management including subscription tracking,
member management, and usage limits.
"""

from typing import List, Optional
from datetime import datetime

from sqlalchemy import and_, func
from sqlalchemy.orm import Session

from app.crud.base import CRUDBase
from app.db.models.organization import Organization
from app.db.models.user import User
from app.schemas.organization import OrganizationCreate, OrganizationUpdate


class CRUDOrganization(CRUDBase[Organization, OrganizationCreate, OrganizationUpdate]):
    """
    CRUD operations for Organization model.
    
    Extends base CRUD with organization-specific methods
    for subscription management and member handling.
    """

    def get_by_name(self, db: Session, *, name: str) -> Optional[Organization]:
        """
        Get organization by name.
        
        Args:
            db: Database session
            name: Organization name
            
        Returns:
            Organization if found, None otherwise
        """
        return db.query(Organization).filter(Organization.name == name).first()

    def get_by_subdomain(self, db: Session, *, subdomain: str) -> Optional[Organization]:
        """
        Get organization by subdomain.
        
        Args:
            db: Database session
            subdomain: Organization subdomain
            
        Returns:
            Organization if found, None otherwise
        """
        return db.query(Organization).filter(Organization.subdomain == subdomain).first()

    def get_active_organizations(
        self, db: Session, *, skip: int = 0, limit: int = 100
    ) -> List[Organization]:
        """
        Get active organizations.
        
        Args:
            db: Database session
            skip: Number of records to skip
            limit: Maximum records to return
            
        Returns:
            List of active organizations
        """
        return (
            db.query(Organization)
            .filter(Organization.is_active == True)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_by_subscription_tier(
        self, db: Session, *, tier: str, skip: int = 0, limit: int = 100
    ) -> List[Organization]:
        """
        Get organizations by subscription tier.
        
        Args:
            db: Database session
            tier: Subscription tier (free, basic, premium, enterprise)
            skip: Number of records to skip
            limit: Maximum records to return
            
        Returns:
            List of organizations with matching tier
        """
        return (
            db.query(Organization)
            .filter(Organization.subscription_tier == tier)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_expired_subscriptions(self, db: Session) -> List[Organization]:
        """
        Get organizations with expired subscriptions.
        
        Args:
            db: Database session
            
        Returns:
            List of organizations with expired subscriptions
        """
        return (
            db.query(Organization)
            .filter(
                and_(
                    Organization.subscription_expires_at.isnot(None),
                    Organization.subscription_expires_at < datetime.utcnow()
                )
            )
            .all()
        )

    def get_member_count(self, db: Session, *, organization_id: int) -> int:
        """
        Get number of members in organization.
        
        Args:
            db: Database session
            organization_id: Organization ID
            
        Returns:
            Number of active members
        """
        return (
            db.query(func.count(User.id))
            .filter(
                and_(
                    User.organization_id == organization_id,
                    User.is_active == True
                )
            )
            .scalar()
        )

    def can_add_member(self, db: Session, *, organization_id: int) -> bool:
        """
        Check if organization can add a new member.
        
        Args:
            db: Database session
            organization_id: Organization ID
            
        Returns:
            True if organization can add members, False otherwise
        """
        org = self.get(db, id=organization_id)
        if not org:
            return False
        
        current_members = self.get_member_count(db, organization_id=organization_id)
        
        # Check against member limit
        if org.max_members and current_members >= org.max_members:
            return False
        
        return True

    def update_subscription(
        self,
        db: Session,
        *,
        organization_id: int,
        tier: str,
        expires_at: Optional[datetime] = None,
        max_members: Optional[int] = None,
        max_projects: Optional[int] = None,
        max_calculations_per_month: Optional[int] = None
    ) -> Organization:
        """
        Update organization subscription.
        
        Args:
            db: Database session
            organization_id: Organization ID
            tier: New subscription tier
            expires_at: Subscription expiration date
            max_members: Maximum members allowed
            max_projects: Maximum projects allowed
            max_calculations_per_month: Maximum calculations per month
            
        Returns:
            Updated organization
            
        Raises:
            ValueError: If organization not found
        """
        org = self.get_or_404(db, id=organization_id)
        
        org.subscription_tier = tier
        org.subscription_expires_at = expires_at
        
        if max_members is not None:
            org.max_members = max_members
        if max_projects is not None:
            org.max_projects = max_projects
        if max_calculations_per_month is not None:
            org.max_calculations_per_month = max_calculations_per_month
        
        db.add(org)
        db.commit()
        db.refresh(org)
        return org

    def reset_monthly_usage(self, db: Session, *, organization_id: int) -> Organization:
        """
        Reset monthly usage counters.
        
        Args:
            db: Database session
            organization_id: Organization ID
            
        Returns:
            Updated organization
        """
        org = self.get_or_404(db, id=organization_id)
        
        org.calculations_this_month = 0
        
        db.add(org)
        db.commit()
        db.refresh(org)
        return org

    def increment_calculation_usage(
        self, db: Session, *, organization_id: int
    ) -> Organization:
        """
        Increment calculation usage counter.
        
        Args:
            db: Database session
            organization_id: Organization ID
            
        Returns:
            Updated organization
        """
        org = self.get_or_404(db, id=organization_id)
        
        org.calculations_this_month = (org.calculations_this_month or 0) + 1
        
        db.add(org)
        db.commit()
        db.refresh(org)
        return org

    def can_run_calculation(self, db: Session, *, organization_id: int) -> bool:
        """
        Check if organization can run another calculation.
        
        Args:
            db: Database session
            organization_id: Organization ID
            
        Returns:
            True if organization can run calculations, False otherwise
        """
        org = self.get(db, id=organization_id)
        if not org:
            return False
        
        # Check if organization is active
        if not org.is_active:
            return False
        
        # Check subscription expiration
        if org.subscription_expires_at and org.subscription_expires_at < datetime.utcnow():
            return False
        
        # Check monthly calculation limit
        if (org.max_calculations_per_month and 
            org.calculations_this_month and
            org.calculations_this_month >= org.max_calculations_per_month):
            return False
        
        return True

    def search(
        self,
        db: Session,
        *,
        query: str,
        skip: int = 0,
        limit: int = 100
    ) -> List[Organization]:
        """
        Search organizations by name or description.
        
        Args:
            db: Database session
            query: Search query
            skip: Number of records to skip
            limit: Maximum records to return
            
        Returns:
            List of matching organizations
        """
        search_term = f"%{query}%"
        return (
            db.query(Organization)
            .filter(
                Organization.name.ilike(search_term) |
                Organization.description.ilike(search_term)
            )
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_organizations_by_admin(
        self, db: Session, *, admin_id: int, skip: int = 0, limit: int = 100
    ) -> List[Organization]:
        """
        Get organizations where user is admin.
        
        Args:
            db: Database session
            admin_id: User ID
            skip: Number of records to skip
            limit: Maximum records to return
            
        Returns:
            List of organizations where user is admin
        """
        return (
            db.query(Organization)
            .join(User, User.organization_id == Organization.id)
            .filter(
                and_(
                    User.id == admin_id,
                    User.role.in_(["organization_admin", "super_admin"])
                )
            )
            .offset(skip)
            .limit(limit)
            .all()
        )

    def deactivate(self, db: Session, *, organization_id: int) -> Organization:
        """
        Deactivate organization and all its members.
        
        Args:
            db: Database session
            organization_id: Organization ID
            
        Returns:
            Deactivated organization
        """
        org = self.get_or_404(db, id=organization_id)
        
        # Deactivate organization
        org.is_active = False
        
        # Deactivate all members
        db.query(User).filter(User.organization_id == organization_id).update(
            {"is_active": False}
        )
        
        db.add(org)
        db.commit()
        db.refresh(org)
        return org

    def reactivate(self, db: Session, *, organization_id: int) -> Organization:
        """
        Reactivate organization.
        
        Note: Members need to be reactivated individually.
        
        Args:
            db: Database session
            organization_id: Organization ID
            
        Returns:
            Reactivated organization
        """
        org = self.get_or_404(db, id=organization_id)
        
        org.is_active = True
        
        db.add(org)
        db.commit()
        db.refresh(org)
        return org


# Create instance for dependency injection
organization = CRUDOrganization(Organization)
