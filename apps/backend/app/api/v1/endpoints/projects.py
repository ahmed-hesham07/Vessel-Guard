"""
Project API endpoints.

Handles project management including timeline tracking,
collaboration, and organization-based access control.
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
from app.crud import project as project_crud
from app.db.models.user import User
from app.schemas import (
    Project,
    ProjectCreate,
    ProjectUpdate,
    ProjectWithStats,
    ProjectList,
    ProjectSummary,
    ProjectStatusUpdate,
    ProjectStatistics,
    ProjectDashboard
)

router = APIRouter()


@router.get("/", response_model=ProjectList)
def get_projects(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    search: Optional[str] = Query(None, min_length=1),
    status: Optional[str] = Query(None),
    active_only: bool = Query(True),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get projects in user's organization.
    
    Supports filtering by status and search.
    """
    if not current_user.organization_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User is not associated with any organization"
        )
    
    # Apply filters
    if search:
        projects = project_crud.search(
            db, query=search, organization_id=current_user.organization_id, skip=skip, limit=limit
        )
        total = len(project_crud.search(
            db, query=search, organization_id=current_user.organization_id, skip=0, limit=10000
        ))
    elif status:
        projects = project_crud.get_by_status(
            db, status=status, organization_id=current_user.organization_id, skip=skip, limit=limit
        )
        total = len(project_crud.get_by_status(
            db, status=status, organization_id=current_user.organization_id, skip=0, limit=10000
        ))
    elif active_only:
        projects = project_crud.get_active_by_organization(
            db, organization_id=current_user.organization_id, skip=skip, limit=limit
        )
        total = len(project_crud.get_active_by_organization(
            db, organization_id=current_user.organization_id, skip=0, limit=10000
        ))
    else:
        projects = project_crud.get_by_organization(
            db, organization_id=current_user.organization_id, skip=skip, limit=limit
        )
        total = project_crud.get_project_count_by_organization(
            db, organization_id=current_user.organization_id
        )
    
    return ProjectList(
        items=projects,
        total=total,
        page=skip // limit + 1,
        per_page=limit,
        pages=(total + limit - 1) // limit
    )


@router.post("/", response_model=Project, status_code=status.HTTP_201_CREATED)
def create_project(
    project_in: ProjectCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["engineer", "organization_admin", "super_admin"]))
):
    """
    Create new project.
    
    Engineers and admins can create projects in their organization.
    """
    if not current_user.organization_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User is not associated with any organization"
        )
    
    # Check if organization can create more projects
    if not project_crud.can_create_project(db, organization_id=current_user.organization_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Organization has reached its project limit"
        )
    
    # Check if project number already exists in organization
    if project_in.project_number:
        existing_project = project_crud.get_by_project_number(
            db, 
            project_number=project_in.project_number,
            organization_id=current_user.organization_id
        )
        if existing_project:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Project with this project number already exists in organization"
            )
    
    # Create project data
    project_data = project_in.dict()
    project_data.update({
        "organization_id": current_user.organization_id,
        "created_by_id": current_user.id
    })
    
    project = project_crud.create(db, obj_in=project_data)
    return project


@router.get("/dashboard", response_model=ProjectDashboard)
def get_project_dashboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get project dashboard data for user's organization.
    """
    if not current_user.organization_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User is not associated with any organization"
        )
    
    # Get recent projects
    recent_projects = project_crud.get_recent_projects(
        db, organization_id=current_user.organization_id, limit=5
    )
    
    # Get overdue projects
    overdue_projects = project_crud.get_overdue_projects(
        db, organization_id=current_user.organization_id
    )
    
    # Get projects due soon
    due_soon_projects = project_crud.get_due_soon(
        db, organization_id=current_user.organization_id, days_ahead=7
    )
    
    # Get statistics
    statistics = project_crud.get_project_statistics(
        db, organization_id=current_user.organization_id
    )
    
    return ProjectDashboard(
        recent_projects=[ProjectSummary.from_orm(p) for p in recent_projects],
        overdue_projects=[ProjectSummary.from_orm(p) for p in overdue_projects],
        due_soon_projects=[ProjectSummary.from_orm(p) for p in due_soon_projects],
        statistics=ProjectStatistics(**statistics),
        timeline_overview=[]  # TODO: Implement timeline overview
    )


@router.get("/statistics", response_model=ProjectStatistics)
def get_project_statistics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get project statistics for user's organization.
    """
    if not current_user.organization_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User is not associated with any organization"
        )
    
    statistics = project_crud.get_project_statistics(
        db, organization_id=current_user.organization_id
    )
    
    return ProjectStatistics(**statistics)


@router.get("/overdue", response_model=List[ProjectSummary])
def get_overdue_projects(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get overdue projects in user's organization.
    """
    if not current_user.organization_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User is not associated with any organization"
        )
    
    projects = project_crud.get_overdue_projects(
        db, organization_id=current_user.organization_id
    )
    
    return [ProjectSummary.from_orm(p) for p in projects]


@router.get("/due-soon", response_model=List[ProjectSummary])
def get_due_soon_projects(
    days_ahead: int = Query(7, ge=1, le=365),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get projects due soon in user's organization.
    """
    if not current_user.organization_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User is not associated with any organization"
        )
    
    projects = project_crud.get_due_soon(
        db, organization_id=current_user.organization_id, days_ahead=days_ahead
    )
    
    return [ProjectSummary.from_orm(p) for p in projects]


@router.get("/{project_id}", response_model=Project)
def get_project(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get project by ID.
    
    Users can only access projects in their organization.
    """
    project = project_crud.get(db, id=project_id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    # Check permissions
    if (current_user.role != "super_admin" and 
        project.organization_id != current_user.organization_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to access this project"
        )
    
    return project


@router.put("/{project_id}", response_model=Project)
def update_project(
    project_id: int,
    project_in: ProjectUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["engineer", "organization_admin", "super_admin"]))
):
    """
    Update project.
    
    Engineers and admins can update projects in their organization.
    """
    project = project_crud.get(db, id=project_id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    # Check permissions
    if (current_user.role != "super_admin" and 
        project.organization_id != current_user.organization_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to update this project"
        )
    
    # Check for project number conflicts
    if (project_in.project_number and 
        project_in.project_number != project.project_number):
        existing_project = project_crud.get_by_project_number(
            db,
            project_number=project_in.project_number,
            organization_id=project.organization_id
        )
        if existing_project:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Project with this project number already exists in organization"
            )
    
    # Add updated_by information
    update_data = project_in.dict(exclude_unset=True)
    update_data["updated_by_id"] = current_user.id
    
    project = project_crud.update(db, db_obj=project, obj_in=update_data)
    return project


@router.put("/{project_id}/status", response_model=Project)
def update_project_status(
    project_id: int,
    status_in: ProjectStatusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["engineer", "organization_admin", "super_admin"]))
):
    """
    Update project status.
    """
    project = project_crud.get(db, id=project_id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    # Check permissions
    if (current_user.role != "super_admin" and 
        project.organization_id != current_user.organization_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to update this project"
        )
    
    project = project_crud.update_status(
        db, 
        project_id=project_id,
        status=status_in.status,
        updated_by_id=current_user.id
    )
    
    return project


@router.post("/{project_id}/complete", response_model=Project)
def complete_project(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["engineer", "organization_admin", "super_admin"]))
):
    """
    Mark project as completed.
    """
    project = project_crud.get(db, id=project_id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    # Check permissions
    if (current_user.role != "super_admin" and 
        project.organization_id != current_user.organization_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to complete this project"
        )
    
    project = project_crud.complete_project(
        db, project_id=project_id, completed_by_id=current_user.id
    )
    
    return project


@router.delete("/{project_id}", response_model=Project)
def deactivate_project(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["organization_admin", "super_admin"]))
):
    """
    Deactivate project (soft delete).
    
    Only organization admins and super admins can deactivate projects.
    """
    project = project_crud.get(db, id=project_id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    # Check permissions
    if (current_user.role != "super_admin" and 
        project.organization_id != current_user.organization_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to deactivate this project"
        )
    
    project = project_crud.soft_delete(db, id=project_id)
    return project


@router.get("/statuses/available", response_model=List[str])
def get_available_statuses():
    """
    Get available project statuses.
    """
    return ["planning", "in_progress", "review", "completed", "cancelled", "on_hold"]
