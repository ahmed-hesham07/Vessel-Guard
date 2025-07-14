"""
Vessel API endpoints.

Handles pressure vessel management including design parameters,
inspection tracking, and engineering calculations.
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
from app.crud import vessel as vessel_crud
from app.db.models.user import User
from app.schemas import (
    Vessel,
    VesselCreate,
    VesselUpdate,
    VesselWithStats,
    VesselList,
    VesselSummary,
    VesselInspectionUpdate,
    VesselStatistics,
    VesselDashboard,
    VesselInspectionSchedule
)

router = APIRouter()


@router.get("/", response_model=VesselList)
def get_vessels(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    search: Optional[str] = Query(None, min_length=1),
    vessel_type: Optional[str] = Query(None),
    project_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get vessels in user's organization.
    
    Supports filtering by type, project, and search.
    """
    if not current_user.organization_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User is not associated with any organization"
        )
    
    # Apply filters
    if project_id:
        # Verify project belongs to user's organization
        from app.crud import project as project_crud
        project = project_crud.get(db, id=project_id)
        if not project or project.organization_id != current_user.organization_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found"
            )
        
        vessels = vessel_crud.get_by_project(
            db, project_id=project_id, skip=skip, limit=limit
        )
        total = vessel_crud.get_vessel_count_by_project(db, project_id=project_id)
    elif search:
        vessels = vessel_crud.search(
            db, query=search, organization_id=current_user.organization_id, skip=skip, limit=limit
        )
        total = len(vessel_crud.search(
            db, query=search, organization_id=current_user.organization_id, skip=0, limit=10000
        ))
    elif vessel_type:
        vessels = vessel_crud.get_by_vessel_type(
            db, vessel_type=vessel_type, organization_id=current_user.organization_id, skip=skip, limit=limit
        )
        total = len(vessel_crud.get_by_vessel_type(
            db, vessel_type=vessel_type, organization_id=current_user.organization_id, skip=0, limit=10000
        ))
    else:
        vessels = vessel_crud.get_by_organization(
            db, organization_id=current_user.organization_id, skip=skip, limit=limit
        )
        total = vessel_crud.get_vessel_count_by_organization(
            db, organization_id=current_user.organization_id
        )
    
    return VesselList(
        items=vessels,
        total=total,
        page=skip // limit + 1,
        per_page=limit,
        pages=(total + limit - 1) // limit
    )


@router.post("/", response_model=Vessel, status_code=status.HTTP_201_CREATED)
def create_vessel(
    vessel_in: VesselCreate,
    project_id: int = Query(..., description="Project ID for the vessel"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["engineer", "organization_admin", "super_admin"]))
):
    """
    Create new vessel.
    
    Engineers and admins can create vessels in their organization's projects.
    """
    if not current_user.organization_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User is not associated with any organization"
        )
    
    # Verify project exists and belongs to user's organization
    from app.crud import project as project_crud
    project = project_crud.get(db, id=project_id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    if project.organization_id != current_user.organization_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Project does not belong to your organization"
        )
    
    # Check if tag number already exists in organization
    existing_vessel = vessel_crud.get_by_tag_number(
        db, 
        tag_number=vessel_in.tag_number,
        organization_id=current_user.organization_id
    )
    if existing_vessel:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Vessel with this tag number already exists in organization"
        )
    
    # Create vessel data
    vessel_data = vessel_in.dict()
    vessel_data.update({
        "project_id": project_id,
        "organization_id": current_user.organization_id,
        "created_by_id": current_user.id
    })
    
    vessel = vessel_crud.create(db, obj_in=vessel_data)
    return vessel


@router.get("/dashboard", response_model=VesselDashboard)
def get_vessel_dashboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get vessel dashboard data for user's organization.
    """
    if not current_user.organization_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User is not associated with any organization"
        )
    
    # Get critical vessels
    critical_vessels = vessel_crud.get_critical_vessels(
        db, organization_id=current_user.organization_id
    )
    
    # Get overdue inspections
    overdue_inspections = vessel_crud.get_overdue_for_inspection(
        db, organization_id=current_user.organization_id
    )
    
    # Get inspections due soon
    due_soon_inspections = vessel_crud.get_due_for_inspection(
        db, organization_id=current_user.organization_id, days_ahead=30
    )
    
    # Get statistics
    statistics = vessel_crud.get_vessel_statistics(
        db, organization_id=current_user.organization_id
    )
    
    # Convert to inspection schedule format
    def vessel_to_inspection_schedule(vessel):
        from datetime import datetime
        days_until = None
        is_overdue = False
        
        if vessel.next_inspection_date:
            delta = vessel.next_inspection_date - datetime.utcnow()
            days_until = delta.days
            is_overdue = days_until < 0
        
        return VesselInspectionSchedule(
            vessel_id=vessel.id,
            tag_number=vessel.tag_number,
            name=vessel.name,
            last_inspection_date=vessel.last_inspection_date,
            next_inspection_date=vessel.next_inspection_date,
            days_until_inspection=days_until,
            is_overdue=is_overdue,
            inspection_type="Regulatory",
            priority="High" if is_overdue else "Medium"
        )
    
    return VesselDashboard(
        critical_vessels=[VesselSummary.from_orm(v) for v in critical_vessels],
        overdue_inspections=[vessel_to_inspection_schedule(v) for v in overdue_inspections],
        due_soon_inspections=[vessel_to_inspection_schedule(v) for v in due_soon_inspections],
        statistics=VesselStatistics(**statistics)
    )


@router.get("/statistics", response_model=VesselStatistics)
def get_vessel_statistics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get vessel statistics for user's organization.
    """
    if not current_user.organization_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User is not associated with any organization"
        )
    
    statistics = vessel_crud.get_vessel_statistics(
        db, organization_id=current_user.organization_id
    )
    
    return VesselStatistics(**statistics)


@router.get("/critical", response_model=List[VesselSummary])
def get_critical_vessels(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get critical vessels that require immediate attention.
    """
    if not current_user.organization_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User is not associated with any organization"
        )
    
    vessels = vessel_crud.get_critical_vessels(
        db, organization_id=current_user.organization_id
    )
    
    return [VesselSummary.from_orm(v) for v in vessels]


@router.get("/inspections/overdue", response_model=List[VesselInspectionSchedule])
def get_overdue_inspections(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get vessels overdue for inspection.
    """
    if not current_user.organization_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User is not associated with any organization"
        )
    
    vessels = vessel_crud.get_overdue_for_inspection(
        db, organization_id=current_user.organization_id
    )
    
    def vessel_to_schedule(vessel):
        from datetime import datetime
        days_until = None
        if vessel.next_inspection_date:
            delta = vessel.next_inspection_date - datetime.utcnow()
            days_until = delta.days
        
        return VesselInspectionSchedule(
            vessel_id=vessel.id,
            tag_number=vessel.tag_number,
            name=vessel.name,
            last_inspection_date=vessel.last_inspection_date,
            next_inspection_date=vessel.next_inspection_date,
            days_until_inspection=days_until,
            is_overdue=True,
            inspection_type="Regulatory",
            priority="High"
        )
    
    return [vessel_to_schedule(v) for v in vessels]


@router.get("/inspections/due-soon", response_model=List[VesselInspectionSchedule])
def get_due_soon_inspections(
    days_ahead: int = Query(30, ge=1, le=365),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get vessels due for inspection soon.
    """
    if not current_user.organization_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User is not associated with any organization"
        )
    
    vessels = vessel_crud.get_due_for_inspection(
        db, organization_id=current_user.organization_id, days_ahead=days_ahead
    )
    
    def vessel_to_schedule(vessel):
        from datetime import datetime
        days_until = None
        if vessel.next_inspection_date:
            delta = vessel.next_inspection_date - datetime.utcnow()
            days_until = delta.days
        
        return VesselInspectionSchedule(
            vessel_id=vessel.id,
            tag_number=vessel.tag_number,
            name=vessel.name,
            last_inspection_date=vessel.last_inspection_date,
            next_inspection_date=vessel.next_inspection_date,
            days_until_inspection=days_until,
            is_overdue=False,
            inspection_type="Regulatory",
            priority="Medium"
        )
    
    return [vessel_to_schedule(v) for v in vessels]


@router.get("/search/by-pressure", response_model=List[Vessel])
def search_vessels_by_pressure(
    min_pressure: Optional[float] = Query(None, ge=0),
    max_pressure: Optional[float] = Query(None, ge=0),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Search vessels by operating pressure range.
    """
    if not current_user.organization_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User is not associated with any organization"
        )
    
    vessels = vessel_crud.get_by_pressure_range(
        db,
        min_pressure=min_pressure,
        max_pressure=max_pressure,
        organization_id=current_user.organization_id,
        skip=skip,
        limit=limit
    )
    
    return vessels


@router.get("/search/by-temperature", response_model=List[Vessel])
def search_vessels_by_temperature(
    min_temperature: Optional[float] = Query(None),
    max_temperature: Optional[float] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Search vessels by operating temperature range.
    """
    if not current_user.organization_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User is not associated with any organization"
        )
    
    vessels = vessel_crud.get_by_temperature_range(
        db,
        min_temperature=min_temperature,
        max_temperature=max_temperature,
        organization_id=current_user.organization_id,
        skip=skip,
        limit=limit
    )
    
    return vessels


@router.get("/{vessel_id}", response_model=Vessel)
def get_vessel(
    vessel_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get vessel by ID.
    
    Users can only access vessels in their organization.
    """
    vessel = vessel_crud.get(db, id=vessel_id)
    if not vessel:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vessel not found"
        )
    
    # Check permissions
    if (current_user.role != "super_admin" and 
        vessel.organization_id != current_user.organization_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to access this vessel"
        )
    
    return vessel


@router.put("/{vessel_id}", response_model=Vessel)
def update_vessel(
    vessel_id: int,
    vessel_in: VesselUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["engineer", "organization_admin", "super_admin"]))
):
    """
    Update vessel.
    
    Engineers and admins can update vessels in their organization.
    """
    vessel = vessel_crud.get(db, id=vessel_id)
    if not vessel:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vessel not found"
        )
    
    # Check permissions
    if (current_user.role != "super_admin" and 
        vessel.organization_id != current_user.organization_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to update this vessel"
        )
    
    # Check for tag number conflicts
    if (vessel_in.tag_number and 
        vessel_in.tag_number != vessel.tag_number):
        existing_vessel = vessel_crud.get_by_tag_number(
            db,
            tag_number=vessel_in.tag_number,
            organization_id=vessel.organization_id
        )
        if existing_vessel:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Vessel with this tag number already exists in organization"
            )
    
    # Add updated_by information
    update_data = vessel_in.dict(exclude_unset=True)
    update_data["updated_by_id"] = current_user.id
    
    vessel = vessel_crud.update(db, db_obj=vessel, obj_in=update_data)
    return vessel


@router.put("/{vessel_id}/inspection", response_model=Vessel)
def update_vessel_inspection(
    vessel_id: int,
    inspection_in: VesselInspectionUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["engineer", "organization_admin", "super_admin"]))
):
    """
    Update vessel inspection dates.
    """
    vessel = vessel_crud.get(db, id=vessel_id)
    if not vessel:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vessel not found"
        )
    
    # Check permissions
    if (current_user.role != "super_admin" and 
        vessel.organization_id != current_user.organization_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to update this vessel"
        )
    
    # Update inspection dates
    update_data = inspection_in.dict(exclude_unset=True)
    update_data["updated_by_id"] = current_user.id
    
    vessel = vessel_crud.update(db, db_obj=vessel, obj_in=update_data)
    return vessel


@router.delete("/{vessel_id}", response_model=Vessel)
def deactivate_vessel(
    vessel_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["organization_admin", "super_admin"]))
):
    """
    Deactivate vessel (soft delete).
    
    Only organization admins and super admins can deactivate vessels.
    """
    vessel = vessel_crud.get(db, id=vessel_id)
    if not vessel:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vessel not found"
        )
    
    # Check permissions
    if (current_user.role != "super_admin" and 
        vessel.organization_id != current_user.organization_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to deactivate this vessel"
        )
    
    vessel = vessel_crud.soft_delete(db, id=vessel_id)
    return vessel


@router.get("/types/available", response_model=List[str])
def get_available_vessel_types():
    """
    Get available vessel types.
    """
    return [
        "pressure_vessel", "storage_tank", "heat_exchanger", 
        "reactor", "column", "separator", "filter", "other"
    ]


@router.get("/codes/available", response_model=List[str])
def get_available_design_codes():
    """
    Get available design codes.
    """
    return [
        "ASME VIII Div 1", "ASME VIII Div 2", "ASME I", 
        "API 650", "API 620", "PD 5500", "EN 13445", "Other"
    ]
