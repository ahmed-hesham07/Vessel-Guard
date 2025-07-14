"""
Organization API endpoints.

Handles organization management, subscription tracking,
and member administration.
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
from app.crud import organization as org_crud
from app.db.models.user import User
from app.schemas import (
    Organization,
    OrganizationCreate,
    OrganizationUpdate,
    OrganizationWithStats,
    OrganizationList,
    OrganizationSummary,
    OrganizationSubscriptionUpdate,
    OrganizationUsageStats
)

router = APIRouter()


@router.get("/", response_model=OrganizationList)
def get_organizations(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    search: Optional[str] = Query(None, min_length=1),
    tier: Optional[str] = Query(None),
    active_only: bool = Query(True),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["super_admin"]))
):
    """
    Get all organizations (Super Admin only).
    
    Supports filtering by subscription tier and search.
    """
    if search:
        organizations = org_crud.search(
            db, query=search, skip=skip, limit=limit
        )
        total = len(org_crud.search(db, query=search, skip=0, limit=10000))
    elif tier:
        organizations = org_crud.get_by_subscription_tier(
            db, tier=tier, skip=skip, limit=limit
        )
        total = len(org_crud.get_by_subscription_tier(db, tier=tier, skip=0, limit=10000))
    elif active_only:
        organizations = org_crud.get_active_organizations(
            db, skip=skip, limit=limit
        )
        total = len(org_crud.get_active_organizations(db, skip=0, limit=10000))
    else:
        organizations = org_crud.get_multi(db, skip=skip, limit=limit)
        total = org_crud.count(db)
    
    return OrganizationList(
        items=organizations,
        total=total,
        page=skip // limit + 1,
        per_page=limit,
        pages=(total + limit - 1) // limit
    )


@router.post("/", response_model=Organization, status_code=status.HTTP_201_CREATED)
def create_organization(
    organization_in: OrganizationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["super_admin", "organization_admin"]))
):
    """
    Create new organization.
    
    Super admins can create any organization.
    Organization admins can only create organizations they will manage.
    """
    # Check if organization name already exists
    existing_org = org_crud.get_by_name(db, name=organization_in.name)
    if existing_org:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Organization with this name already exists"
        )
    
    # Check if subdomain already exists
    if organization_in.subdomain:
        existing_subdomain = org_crud.get_by_subdomain(db, subdomain=organization_in.subdomain)
        if existing_subdomain:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Organization with this subdomain already exists"
            )
    
    organization = org_crud.create(db, obj_in=organization_in)
    
    # If current user is not super admin, assign them as organization admin
    if current_user.role != "super_admin":
        from app.crud import user as user_crud
        user_crud.update(
            db,
            db_obj=current_user,
            obj_in={"organization_id": organization.id, "role": "organization_admin"}
        )
    
    return organization


@router.get("/me", response_model=OrganizationWithStats)
def get_my_organization(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get current user's organization with statistics.
    """
    if not current_user.organization_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User is not associated with any organization"
        )
    
    organization = org_crud.get(db, id=current_user.organization_id)
    if not organization:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization not found"
        )
    
    # Get statistics
    member_count = org_crud.get_member_count(db, organization_id=organization.id)
    
    from app.crud import project as project_crud
    project_count = project_crud.get_project_count_by_organization(
        db, organization_id=organization.id
    )
    
    # Calculate calculation usage percentage
    calculation_usage_percentage = 0.0
    if organization.max_calculations_per_month and organization.calculations_this_month:
        calculation_usage_percentage = (
            organization.calculations_this_month / organization.max_calculations_per_month * 100
        )
    
    # Convert to response model with stats
    org_dict = organization.__dict__.copy()
    org_dict.update({
        "member_count": member_count,
        "project_count": project_count,
        "calculation_usage_percentage": calculation_usage_percentage
    })
    
    return OrganizationWithStats(**org_dict)


@router.get("/usage-stats", response_model=OrganizationUsageStats)
def get_organization_usage_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["organization_admin", "super_admin"]))
):
    """
    Get organization usage statistics.
    """
    organization_id = current_user.organization_id
    if current_user.role == "super_admin":
        # Super admin needs to specify organization_id in query params
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Super admin must specify organization_id as query parameter"
        )
    
    if not organization_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User is not associated with any organization"
        )
    
    organization = org_crud.get(db, id=organization_id)
    if not organization:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization not found"
        )
    
    # Get usage statistics
    member_count = org_crud.get_member_count(db, organization_id=organization_id)
    
    from app.crud import project as project_crud
    project_count = project_crud.get_project_count_by_organization(
        db, organization_id=organization_id
    )
    
    calculations_remaining = None
    if organization.max_calculations_per_month:
        calculations_remaining = (
            organization.max_calculations_per_month - (organization.calculations_this_month or 0)
        )
    
    days_until_expiration = None
    if organization.subscription_expires_at:
        from datetime import datetime
        delta = organization.subscription_expires_at - datetime.utcnow()
        days_until_expiration = delta.days if delta.days > 0 else 0
    
    return OrganizationUsageStats(
        organization_id=organization_id,
        member_count=member_count,
        project_count=project_count,
        calculations_this_month=organization.calculations_this_month or 0,
        max_calculations_per_month=organization.max_calculations_per_month,
        calculations_remaining=calculations_remaining,
        subscription_tier=organization.subscription_tier,
        subscription_expires_at=organization.subscription_expires_at,
        days_until_expiration=days_until_expiration
    )


@router.get("/{organization_id}", response_model=Organization)
def get_organization(
    organization_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get organization by ID.
    
    Users can only access their own organization unless they are super admin.
    """
    organization = org_crud.get(db, id=organization_id)
    if not organization:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization not found"
        )
    
    # Check permissions
    if current_user.role != "super_admin" and current_user.organization_id != organization_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to access this organization"
        )
    
    return organization


@router.put("/{organization_id}", response_model=Organization)
def update_organization(
    organization_id: int,
    organization_in: OrganizationUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["organization_admin", "super_admin"]))
):
    """
    Update organization.
    
    Organization admins can only update their own organization.
    Super admins can update any organization.
    """
    organization = org_crud.get(db, id=organization_id)
    if not organization:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization not found"
        )
    
    # Check permissions
    if current_user.role != "super_admin" and current_user.organization_id != organization_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to update this organization"
        )
    
    # Check for name conflicts
    if organization_in.name and organization_in.name != organization.name:
        existing_org = org_crud.get_by_name(db, name=organization_in.name)
        if existing_org:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Organization with this name already exists"
            )
    
    # Check for subdomain conflicts
    if organization_in.subdomain and organization_in.subdomain != organization.subdomain:
        existing_subdomain = org_crud.get_by_subdomain(db, subdomain=organization_in.subdomain)
        if existing_subdomain:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Organization with this subdomain already exists"
            )
    
    organization = org_crud.update(db, db_obj=organization, obj_in=organization_in)
    return organization


@router.put("/{organization_id}/subscription", response_model=Organization)
def update_organization_subscription(
    organization_id: int,
    subscription_in: OrganizationSubscriptionUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["super_admin"]))
):
    """
    Update organization subscription (Super Admin only).
    """
    organization = org_crud.get(db, id=organization_id)
    if not organization:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization not found"
        )
    
    organization = org_crud.update_subscription(
        db,
        organization_id=organization_id,
        tier=subscription_in.subscription_tier,
        expires_at=subscription_in.subscription_expires_at,
        max_members=subscription_in.max_members,
        max_projects=subscription_in.max_projects,
        max_calculations_per_month=subscription_in.max_calculations_per_month
    )
    
    return organization


@router.post("/{organization_id}/deactivate", response_model=Organization)
def deactivate_organization(
    organization_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["super_admin"]))
):
    """
    Deactivate organization and all its members (Super Admin only).
    """
    organization = org_crud.get(db, id=organization_id)
    if not organization:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization not found"
        )
    
    organization = org_crud.deactivate(db, organization_id=organization_id)
    return organization


@router.post("/{organization_id}/reactivate", response_model=Organization)
def reactivate_organization(
    organization_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["super_admin"]))
):
    """
    Reactivate organization (Super Admin only).
    """
    organization = org_crud.get(db, id=organization_id)
    if not organization:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization not found"
        )
    
    organization = org_crud.reactivate(db, organization_id=organization_id)
    return organization


@router.post("/{organization_id}/reset-usage", response_model=Organization)
def reset_monthly_usage(
    organization_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["super_admin"]))
):
    """
    Reset monthly usage counters (Super Admin only).
    """
    organization = org_crud.get(db, id=organization_id)
    if not organization:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization not found"
        )
    
    organization = org_crud.reset_monthly_usage(db, organization_id=organization_id)
    return organization


@router.get("/expired/subscriptions", response_model=List[OrganizationSummary])
def get_expired_subscriptions(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["super_admin"]))
):
    """
    Get organizations with expired subscriptions (Super Admin only).
    """
    organizations = org_crud.get_expired_subscriptions(db)
    return [OrganizationSummary.from_orm(org) for org in organizations]
