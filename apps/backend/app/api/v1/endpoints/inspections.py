"""
Inspection API endpoints.

Handles vessel inspection tracking including scheduling,
results recording, and compliance management.
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
from app.crud import inspection as inspection_crud
from app.db.models.user import User
from app.schemas import (
    Inspection,
    InspectionCreate,
    InspectionUpdate,
    InspectionList,
    InspectionSummary,
    InspectionStatistics,
    InspectionDashboard,
    InspectionSchedule,
    InspectionCalendarEvent
)

router = APIRouter()


@router.get("/", response_model=InspectionList)
def get_inspections(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    search: Optional[str] = Query(None, min_length=1),
    inspection_type: Optional[str] = Query(None),
    vessel_id: Optional[int] = Query(None),
    project_id: Optional[int] = Query(None),
    result: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get inspections in user's organization.
    
    Supports filtering by type, vessel, project, result, and search.
    """
    if not current_user.organization_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User is not associated with any organization"
        )
    
    # Apply filters
    if vessel_id:
        # Verify vessel belongs to user's organization
        from app.crud import vessel as vessel_crud
        vessel = vessel_crud.get(db, id=vessel_id)
        if not vessel or vessel.organization_id != current_user.organization_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Vessel not found"
            )
        
        inspections = inspection_crud.get_by_vessel(
            db, vessel_id=vessel_id, skip=skip, limit=limit
        )
        total = inspection_crud.get_inspection_count_by_vessel(db, vessel_id=vessel_id)
    elif project_id:
        # Verify project belongs to user's organization
        from app.crud import project as project_crud
        project = project_crud.get(db, id=project_id)
        if not project or project.organization_id != current_user.organization_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found"
            )
        
        inspections = inspection_crud.get_by_project(
            db, project_id=project_id, skip=skip, limit=limit
        )
        total = len(inspection_crud.get_by_project(
            db, project_id=project_id, skip=0, limit=10000
        ))
    elif search:
        inspections = inspection_crud.search(
            db, query=search, organization_id=current_user.organization_id, skip=skip, limit=limit
        )
        total = len(inspection_crud.search(
            db, query=search, organization_id=current_user.organization_id, skip=0, limit=10000
        ))
    elif inspection_type:
        inspections = inspection_crud.get_by_inspection_type(
            db, inspection_type=inspection_type, organization_id=current_user.organization_id, skip=skip, limit=limit
        )
        total = len(inspection_crud.get_by_inspection_type(
            db, inspection_type=inspection_type, organization_id=current_user.organization_id, skip=0, limit=10000
        ))
    else:
        # Get all inspections for organization
        inspections = []
        total = inspection_crud.get_inspection_count_by_organization(
            db, organization_id=current_user.organization_id
        )
    
    return InspectionList(
        items=inspections,
        total=total,
        page=skip // limit + 1,
        per_page=limit,
        pages=(total + limit - 1) // limit
    )


@router.post("/", response_model=Inspection, status_code=status.HTTP_201_CREATED)
def create_inspection(
    inspection_in: InspectionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["engineer", "organization_admin", "super_admin"]))
):
    """
    Create new inspection.
    
    Engineers and admins can create inspections for vessels in their organization.
    """
    if not current_user.organization_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User is not associated with any organization"
        )
    
    # Verify vessel exists and belongs to user's organization
    from app.crud import vessel as vessel_crud
    vessel = vessel_crud.get(db, id=inspection_in.vessel_id)
    if not vessel:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vessel not found"
        )
    
    if vessel.organization_id != current_user.organization_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Vessel does not belong to your organization"
        )
    
    # Create inspection data
    inspection_data = inspection_in.dict()
    inspection_data.update({
        "created_by_id": current_user.id
    })
    
    inspection = inspection_crud.create(db, obj_in=inspection_data)
    
    # Update vessel's last inspection date if this is the most recent
    if not vessel.last_inspection_date or inspection.inspection_date > vessel.last_inspection_date:
        vessel_update = {
            "last_inspection_date": inspection.inspection_date,
            "next_inspection_date": inspection.next_inspection_date
        }
        vessel_crud.update(db, db_obj=vessel, obj_in=vessel_update)
    
    return inspection


@router.get("/dashboard", response_model=InspectionDashboard)
def get_inspection_dashboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get inspection dashboard data for user's organization.
    """
    if not current_user.organization_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User is not associated with any organization"
        )
    
    # Get recent inspections
    recent_inspections = inspection_crud.get_recent_inspections(
        db, organization_id=current_user.organization_id, days=30, limit=5
    )
    
    # Get overdue inspections
    overdue_inspections = inspection_crud.get_overdue_inspections(
        db, organization_id=current_user.organization_id, skip=0, limit=5
    )
    
    # Get due soon inspections
    due_soon_inspections = inspection_crud.get_due_inspections(
        db, organization_id=current_user.organization_id, days_ahead=30, skip=0, limit=5
    )
    
    # Get failed inspections
    failed_inspections = inspection_crud.get_failed_inspections(
        db, organization_id=current_user.organization_id, skip=0, limit=5
    )
    
    # Get statistics
    statistics = inspection_crud.get_inspection_statistics(
        db, organization_id=current_user.organization_id
    )
    
    return InspectionDashboard(
        recent_inspections=[InspectionSummary.from_orm(i) for i in recent_inspections],
        overdue_inspections=[InspectionSummary.from_orm(i) for i in overdue_inspections],
        due_soon_inspections=[InspectionSummary.from_orm(i) for i in due_soon_inspections],
        failed_inspections=[InspectionSummary.from_orm(i) for i in failed_inspections],
        statistics=InspectionStatistics(**statistics)
    )


@router.get("/statistics", response_model=InspectionStatistics)
def get_inspection_statistics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get inspection statistics for user's organization.
    """
    if not current_user.organization_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User is not associated with any organization"
        )
    
    statistics = inspection_crud.get_inspection_statistics(
        db, organization_id=current_user.organization_id
    )
    
    return InspectionStatistics(**statistics)


@router.get("/schedule", response_model=List[InspectionSchedule])
def get_inspection_schedule(
    days_ahead: int = Query(90, ge=1, le=365),
    include_overdue: bool = Query(True),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get inspection schedule for organization.
    """
    if not current_user.organization_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User is not associated with any organization"
        )
    
    schedule = []
    
    # Get due soon inspections
    due_soon = inspection_crud.get_due_inspections(
        db, organization_id=current_user.organization_id, days_ahead=days_ahead
    )
    
    # Get overdue inspections if requested
    if include_overdue:
        overdue = inspection_crud.get_overdue_inspections(
            db, organization_id=current_user.organization_id
        )
        # Combine and sort by date
        all_inspections = overdue + due_soon
    else:
        all_inspections = due_soon
    
    # Convert to schedule format
    for inspection in all_inspections:
        from datetime import datetime
        days_until = None
        is_overdue = False
        
        if inspection.next_inspection_date:
            delta = inspection.next_inspection_date - datetime.utcnow().date()
            days_until = delta.days
            is_overdue = days_until < 0
        
        # Get vessel info
        from app.crud import vessel as vessel_crud
        vessel = vessel_crud.get(db, id=inspection.vessel_id)
        
        schedule_item = InspectionSchedule(
            vessel_id=inspection.vessel_id,
            vessel_tag_number=vessel.tag_number if vessel else "Unknown",
            vessel_name=vessel.name if vessel else "Unknown",
            last_inspection_date=inspection.inspection_date,
            next_inspection_date=inspection.next_inspection_date,
            days_until_inspection=days_until,
            is_overdue=is_overdue,
            inspection_type=inspection.inspection_type,
            priority="High" if is_overdue else "Medium"
        )
        schedule.append(schedule_item)
    
    # Sort by urgency (overdue first, then by days until)
    schedule.sort(key=lambda x: (not x.is_overdue, x.days_until_inspection or 999))
    
    return schedule


@router.get("/calendar", response_model=List[InspectionCalendarEvent])
def get_inspection_calendar(
    year: int = Query(..., ge=2020, le=2030),
    month: Optional[int] = Query(None, ge=1, le=12),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get inspection calendar events for display.
    """
    if not current_user.organization_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User is not associated with any organization"
        )
    
    from datetime import datetime, date
    import calendar as cal
    
    # Determine date range
    if month:
        start_date = date(year, month, 1)
        _, last_day = cal.monthrange(year, month)
        end_date = date(year, month, last_day)
    else:
        start_date = date(year, 1, 1)
        end_date = date(year, 12, 31)
    
    # Get inspections in date range
    # This would need a new CRUD method to filter by date range
    # For now, get all and filter
    all_inspections = inspection_crud.get_recent_inspections(
        db, organization_id=current_user.organization_id, days=365, limit=1000
    )
    
    events = []
    for inspection in all_inspections:
        if start_date <= inspection.inspection_date <= end_date:
            # Get vessel info
            from app.crud import vessel as vessel_crud
            vessel = vessel_crud.get(db, id=inspection.vessel_id)
            
            event = InspectionCalendarEvent(
                id=inspection.id,
                title=f"{inspection.inspection_type} - {vessel.tag_number if vessel else 'Unknown'}",
                date=inspection.inspection_date,
                vessel_tag_number=vessel.tag_number if vessel else "Unknown",
                inspection_type=inspection.inspection_type,
                is_overdue=False,  # Past inspections are not overdue
                priority="Medium"
            )
            events.append(event)
    
    return events


@router.get("/overdue", response_model=List[InspectionSummary])
def get_overdue_inspections(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=1000),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get overdue inspections that need immediate attention.
    """
    if not current_user.organization_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User is not associated with any organization"
        )
    
    inspections = inspection_crud.get_overdue_inspections(
        db, organization_id=current_user.organization_id, skip=skip, limit=limit
    )
    
    return [InspectionSummary.from_orm(i) for i in inspections]


@router.get("/due-soon", response_model=List[InspectionSummary])
def get_due_soon_inspections(
    days_ahead: int = Query(30, ge=1, le=365),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=1000),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get inspections due soon.
    """
    if not current_user.organization_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User is not associated with any organization"
        )
    
    inspections = inspection_crud.get_due_inspections(
        db, organization_id=current_user.organization_id, days_ahead=days_ahead, skip=skip, limit=limit
    )
    
    return [InspectionSummary.from_orm(i) for i in inspections]


@router.get("/failed", response_model=List[InspectionSummary])
def get_failed_inspections(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=1000),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get failed inspections that need attention.
    """
    if not current_user.organization_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User is not associated with any organization"
        )
    
    inspections = inspection_crud.get_failed_inspections(
        db, organization_id=current_user.organization_id, skip=skip, limit=limit
    )
    
    return [InspectionSummary.from_orm(i) for i in inspections]


@router.get("/{inspection_id}", response_model=Inspection)
def get_inspection(
    inspection_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get inspection by ID.
    
    Users can only access inspections for vessels in their organization.
    """
    inspection = inspection_crud.get(db, id=inspection_id)
    if not inspection:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Inspection not found"
        )
    
    # Check permissions through vessel
    from app.crud import vessel as vessel_crud
    vessel = vessel_crud.get(db, id=inspection.vessel_id)
    if not vessel:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Associated vessel not found"
        )
    
    if (current_user.role != "super_admin" and 
        vessel.organization_id != current_user.organization_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to access this inspection"
        )
    
    return inspection


@router.put("/{inspection_id}", response_model=Inspection)
def update_inspection(
    inspection_id: int,
    inspection_in: InspectionUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["engineer", "organization_admin", "super_admin"]))
):
    """
    Update inspection.
    
    Engineers and admins can update inspections for vessels in their organization.
    """
    inspection = inspection_crud.get(db, id=inspection_id)
    if not inspection:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Inspection not found"
        )
    
    # Check permissions through vessel
    from app.crud import vessel as vessel_crud
    vessel = vessel_crud.get(db, id=inspection.vessel_id)
    if not vessel:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Associated vessel not found"
        )
    
    if (current_user.role != "super_admin" and 
        vessel.organization_id != current_user.organization_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to update this inspection"
        )
    
    # Update inspection
    update_data = inspection_in.dict(exclude_unset=True)
    update_data["updated_by_id"] = current_user.id
    
    inspection = inspection_crud.update(db, db_obj=inspection, obj_in=update_data)
    
    # Update vessel's inspection dates if this is the latest inspection
    latest_inspection = inspection_crud.get_latest_inspection_by_vessel(
        db, vessel_id=inspection.vessel_id
    )
    if latest_inspection and latest_inspection.id == inspection.id:
        vessel_update = {
            "last_inspection_date": inspection.inspection_date,
            "next_inspection_date": inspection.next_inspection_date
        }
        vessel_crud.update(db, db_obj=vessel, obj_in=vessel_update)
    
    return inspection


@router.put("/{inspection_id}/schedule-next", response_model=Inspection)
def schedule_next_inspection(
    inspection_id: int,
    next_inspection_date: str = Query(..., description="Next inspection date (YYYY-MM-DD)"),
    interval_months: Optional[int] = Query(None, ge=1, le=120, description="Inspection interval in months"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["engineer", "organization_admin", "super_admin"]))
):
    """
    Schedule next inspection date.
    """
    inspection = inspection_crud.get(db, id=inspection_id)
    if not inspection:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Inspection not found"
        )
    
    # Check permissions through vessel
    from app.crud import vessel as vessel_crud
    vessel = vessel_crud.get(db, id=inspection.vessel_id)
    if not vessel:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Associated vessel not found"
        )
    
    if (current_user.role != "super_admin" and 
        vessel.organization_id != current_user.organization_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to schedule inspection"
        )
    
    # Parse date
    from datetime import datetime
    try:
        next_date = datetime.strptime(next_inspection_date, "%Y-%m-%d").date()
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid date format. Use YYYY-MM-DD"
        )
    
    # Validate date is in the future
    if next_date <= datetime.utcnow().date():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Next inspection date must be in the future"
        )
    
    # Schedule next inspection
    inspection = inspection_crud.schedule_next_inspection(
        db,
        inspection_id=inspection_id,
        next_inspection_date=next_date,
        interval_months=interval_months
    )
    
    return inspection


@router.delete("/{inspection_id}", response_model=Inspection)
def deactivate_inspection(
    inspection_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["organization_admin", "super_admin"]))
):
    """
    Deactivate inspection (soft delete).
    
    Only organization admins and super admins can deactivate inspections.
    """
    inspection = inspection_crud.get(db, id=inspection_id)
    if not inspection:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Inspection not found"
        )
    
    # Check permissions through vessel
    from app.crud import vessel as vessel_crud
    vessel = vessel_crud.get(db, id=inspection.vessel_id)
    if not vessel:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Associated vessel not found"
        )
    
    if (current_user.role != "super_admin" and 
        vessel.organization_id != current_user.organization_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to deactivate this inspection"
        )
    
    inspection = inspection_crud.soft_delete(db, id=inspection_id)
    return inspection


@router.get("/types/available", response_model=List[str])
def get_available_inspection_types():
    """
    Get available inspection types.
    """
    return [
        "visual", "ultrasonic", "radiographic", "magnetic_particle",
        "liquid_penetrant", "eddy_current", "pressure_test", 
        "leak_test", "thickness_measurement", "regulatory", "other"
    ]
