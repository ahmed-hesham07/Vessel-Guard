"""
Calculation API endpoints.

Handles pressure vessel engineering calculations including
ASME calculations, stress analysis, and design verification.
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
from app.crud import calculation as calculation_crud
from app.db.models.user import User
from app.schemas import (
    Calculation,
    CalculationCreate,
    CalculationUpdate,
    CalculationList,
    CalculationSummary,
    CalculationStatistics,
    CalculationDashboard,
    CalculationResult,
    CalculationReview
)

router = APIRouter()


@router.get("/", response_model=CalculationList)
def get_calculations(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    search: Optional[str] = Query(None, min_length=1),
    calculation_type: Optional[str] = Query(None),
    vessel_id: Optional[int] = Query(None),
    project_id: Optional[int] = Query(None),
    status: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get calculations in user's organization.
    
    Supports filtering by type, vessel, project, status, and search.
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
        
        calculations = calculation_crud.get_by_vessel(
            db, vessel_id=vessel_id, skip=skip, limit=limit
        )
        total = calculation_crud.get_calculation_count_by_vessel(db, vessel_id=vessel_id)
    elif project_id:
        # Verify project belongs to user's organization
        from app.crud import project as project_crud
        project = project_crud.get(db, id=project_id)
        if not project or project.organization_id != current_user.organization_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found"
            )
        
        calculations = calculation_crud.get_by_project(
            db, project_id=project_id, skip=skip, limit=limit
        )
        total = len(calculation_crud.get_by_project(
            db, project_id=project_id, skip=0, limit=10000
        ))
    elif search:
        calculations = calculation_crud.search(
            db, query=search, organization_id=current_user.organization_id, skip=skip, limit=limit
        )
        total = len(calculation_crud.search(
            db, query=search, organization_id=current_user.organization_id, skip=0, limit=10000
        ))
    elif calculation_type:
        calculations = calculation_crud.get_by_calculation_type(
            db, calculation_type=calculation_type, organization_id=current_user.organization_id, skip=skip, limit=limit
        )
        total = len(calculation_crud.get_by_calculation_type(
            db, calculation_type=calculation_type, organization_id=current_user.organization_id, skip=0, limit=10000
        ))
    else:
        # Get all calculations for organization (filtered through vessel relationships)
        calculations = []
        total = 0
        # This would need to be implemented in CRUD to get all org calculations
    
    return CalculationList(
        items=calculations,
        total=total,
        page=skip // limit + 1,
        per_page=limit,
        pages=(total + limit - 1) // limit
    )


@router.post("/", response_model=Calculation, status_code=status.HTTP_201_CREATED)
def create_calculation(
    calculation_in: CalculationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["engineer", "organization_admin", "super_admin"]))
):
    """
    Create new calculation.
    
    Engineers and admins can create calculations for vessels in their organization.
    """
    if not current_user.organization_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User is not associated with any organization"
        )
    
    # Verify vessel exists and belongs to user's organization
    from app.crud import vessel as vessel_crud
    vessel = vessel_crud.get(db, id=calculation_in.vessel_id)
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
    
    # Create calculation data
    calculation_data = calculation_in.dict()
    calculation_data.update({
        "created_by_id": current_user.id,
        "status": "pending"
    })
    
    calculation = calculation_crud.create(db, obj_in=calculation_data)
    return calculation


@router.get("/dashboard", response_model=CalculationDashboard)
def get_calculation_dashboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get calculation dashboard data for user's organization.
    """
    if not current_user.organization_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User is not associated with any organization"
        )
    
    # Get recent calculations
    recent_calculations = calculation_crud.get_recent_calculations(
        db, organization_id=current_user.organization_id, days=30, limit=5
    )
    
    # Get failed calculations
    failed_calculations = calculation_crud.get_failed_calculations(
        db, organization_id=current_user.organization_id, skip=0, limit=5
    )
    
    # Get calculations needing review
    calculations_needing_review = calculation_crud.get_calculations_needing_review(
        db, organization_id=current_user.organization_id, skip=0, limit=5
    )
    
    # Get statistics
    statistics = calculation_crud.get_calculation_statistics(
        db, organization_id=current_user.organization_id
    )
    
    return CalculationDashboard(
        recent_calculations=[CalculationSummary.from_orm(c) for c in recent_calculations],
        failed_calculations=[CalculationSummary.from_orm(c) for c in failed_calculations],
        calculations_needing_review=[CalculationSummary.from_orm(c) for c in calculations_needing_review],
        statistics=CalculationStatistics(**statistics)
    )


@router.get("/statistics", response_model=CalculationStatistics)
def get_calculation_statistics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get calculation statistics for user's organization.
    """
    if not current_user.organization_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User is not associated with any organization"
        )
    
    statistics = calculation_crud.get_calculation_statistics(
        db, organization_id=current_user.organization_id
    )
    
    return CalculationStatistics(**statistics)


@router.get("/failed", response_model=List[CalculationSummary])
def get_failed_calculations(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=1000),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get failed calculations that need attention.
    """
    if not current_user.organization_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User is not associated with any organization"
        )
    
    calculations = calculation_crud.get_failed_calculations(
        db, organization_id=current_user.organization_id, skip=skip, limit=limit
    )
    
    return [CalculationSummary.from_orm(c) for c in calculations]


@router.get("/review-needed", response_model=List[CalculationSummary])
def get_calculations_needing_review(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=1000),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["engineer", "organization_admin", "super_admin"]))
):
    """
    Get calculations that need engineering review.
    """
    if not current_user.organization_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User is not associated with any organization"
        )
    
    calculations = calculation_crud.get_calculations_needing_review(
        db, organization_id=current_user.organization_id, skip=skip, limit=limit
    )
    
    return [CalculationSummary.from_orm(c) for c in calculations]


@router.get("/recent", response_model=List[CalculationSummary])
def get_recent_calculations(
    days: int = Query(30, ge=1, le=365),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get recent calculations for organization.
    """
    if not current_user.organization_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User is not associated with any organization"
        )
    
    calculations = calculation_crud.get_recent_calculations(
        db, organization_id=current_user.organization_id, days=days, limit=limit
    )
    
    return [CalculationSummary.from_orm(c) for c in calculations]


@router.get("/{calculation_id}", response_model=Calculation)
def get_calculation(
    calculation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get calculation by ID.
    
    Users can only access calculations for vessels in their organization.
    """
    calculation = calculation_crud.get(db, id=calculation_id)
    if not calculation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Calculation not found"
        )
    
    # Check permissions through vessel
    from app.crud import vessel as vessel_crud
    vessel = vessel_crud.get(db, id=calculation.vessel_id)
    if not vessel:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Associated vessel not found"
        )
    
    if (current_user.role != "super_admin" and 
        vessel.organization_id != current_user.organization_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to access this calculation"
        )
    
    return calculation


@router.put("/{calculation_id}", response_model=Calculation)
def update_calculation(
    calculation_id: int,
    calculation_in: CalculationUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["engineer", "organization_admin", "super_admin"]))
):
    """
    Update calculation.
    
    Engineers and admins can update calculations for vessels in their organization.
    """
    calculation = calculation_crud.get(db, id=calculation_id)
    if not calculation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Calculation not found"
        )
    
    # Check permissions through vessel
    from app.crud import vessel as vessel_crud
    vessel = vessel_crud.get(db, id=calculation.vessel_id)
    if not vessel:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Associated vessel not found"
        )
    
    if (current_user.role != "super_admin" and 
        vessel.organization_id != current_user.organization_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to update this calculation"
        )
    
    # Update calculation
    update_data = calculation_in.dict(exclude_unset=True)
    calculation = calculation_crud.update(db, db_obj=calculation, obj_in=update_data)
    return calculation


@router.put("/{calculation_id}/review", response_model=Calculation)
def review_calculation(
    calculation_id: int,
    review_in: CalculationReview,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["engineer", "organization_admin", "super_admin"]))
):
    """
    Mark calculation as reviewed by engineer.
    """
    calculation = calculation_crud.get(db, id=calculation_id)
    if not calculation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Calculation not found"
        )
    
    # Check permissions through vessel
    from app.crud import vessel as vessel_crud
    vessel = vessel_crud.get(db, id=calculation.vessel_id)
    if not vessel:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Associated vessel not found"
        )
    
    if (current_user.role != "super_admin" and 
        vessel.organization_id != current_user.organization_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to review this calculation"
        )
    
    if calculation.status != "completed":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only completed calculations can be reviewed"
        )
    
    # Mark as reviewed
    calculation = calculation_crud.mark_as_reviewed(
        db, 
        calculation_id=calculation_id,
        reviewed_by_id=current_user.id,
        review_notes=review_in.review_notes
    )
    
    return calculation


@router.put("/{calculation_id}/status", response_model=Calculation)
def update_calculation_status(
    calculation_id: int,
    status_value: str = Query(..., description="New status"),
    error_message: Optional[str] = Query(None, description="Error message for failed status"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["engineer", "organization_admin", "super_admin"]))
):
    """
    Update calculation status.
    
    Used by calculation engines and engineers to update status.
    """
    calculation = calculation_crud.get(db, id=calculation_id)
    if not calculation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Calculation not found"
        )
    
    # Check permissions through vessel
    from app.crud import vessel as vessel_crud
    vessel = vessel_crud.get(db, id=calculation.vessel_id)
    if not vessel:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Associated vessel not found"
        )
    
    if (current_user.role != "super_admin" and 
        vessel.organization_id != current_user.organization_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to update this calculation"
        )
    
    # Validate status
    allowed_statuses = ["pending", "running", "completed", "failed"]
    if status_value not in allowed_statuses:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Status must be one of: {', '.join(allowed_statuses)}"
        )
    
    # Update status
    calculation = calculation_crud.update_status(
        db, 
        calculation_id=calculation_id,
        status=status_value,
        error_message=error_message
    )
    
    return calculation


@router.delete("/{calculation_id}", response_model=Calculation)
def deactivate_calculation(
    calculation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["organization_admin", "super_admin"]))
):
    """
    Deactivate calculation (soft delete).
    
    Only organization admins and super admins can deactivate calculations.
    """
    calculation = calculation_crud.get(db, id=calculation_id)
    if not calculation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Calculation not found"
        )
    
    # Check permissions through vessel
    from app.crud import vessel as vessel_crud
    vessel = vessel_crud.get(db, id=calculation.vessel_id)
    if not vessel:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Associated vessel not found"
        )
    
    if (current_user.role != "super_admin" and 
        vessel.organization_id != current_user.organization_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to deactivate this calculation"
        )
    
    calculation = calculation_crud.soft_delete(db, id=calculation_id)
    return calculation


@router.get("/types/available", response_model=List[str])
def get_available_calculation_types():
    """
    Get available calculation types.
    """
    return [
        "pressure_vessel", "stress_analysis", "fatigue_analysis",
        "thermal_stress", "nozzle_reinforcement", "flange_design",
        "support_design", "seismic_analysis", "wind_load", "other"
    ]
