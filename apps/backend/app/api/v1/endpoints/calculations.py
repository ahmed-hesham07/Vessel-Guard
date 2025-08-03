"""
Calculation endpoints for engineering analysis.

Provides comprehensive calculation management including
ASME, API, and European standards compliance.
"""

from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

from app.api.dependencies import get_current_user, get_db
from app.schemas.calculation import (
    CalculationCreate,
    CalculationUpdate,
    CalculationResponse,
    CalculationListResponse,
    CalculationResultResponse,
    CalculationBulkCreate,
    CalculationBulkResponse
)
from app.crud.calculation import calculation_crud
from app.services.calculation_service import CalculationService
from app.services.validation_service import ValidationService
from app.utils.error_handling import (
    raise_not_found,
    raise_validation_error,
    raise_business_rule_violation
)
from app.utils.engineering import EngineeringUtils
from app.core.logging_config import get_logger

logger = get_logger(__name__)

router = APIRouter()

@router.post("/", response_model=CalculationResponse)
async def create_calculation(
    calculation_data: CalculationCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Create a new engineering calculation.
    
    Validates input parameters and initiates calculation process.
    """
    try:
        # Validate calculation parameters
        validation_service = ValidationService()
        validation_result = validation_service.validate_calculation_parameters(
            calculation_data.input_parameters,
            calculation_data.calculation_type
        )
        
        if not validation_result["valid"]:
            raise_validation_error(
                f"Calculation parameters validation failed: {', '.join(validation_result['errors'])}"
            )
        
        # Check user permissions
        if not current_user.can_perform_calculations:
            raise_business_rule_violation(
                "User does not have permission to perform calculations",
                rule_name="calculation_permission"
            )
        
        # Create calculation
        calculation = calculation_crud.create(
            db=db,
            obj_in=calculation_data,
            user_id=current_user.id
        )
        
        # Log calculation creation
        logger.info(
            f"Calculation created: {calculation.id} by user {current_user.id}",
            extra={
                "calculation_id": calculation.id,
                "calculation_type": calculation.calculation_type,
                "user_id": current_user.id,
                "project_id": calculation.project_id
            }
        )
        
        return calculation

    except Exception as e:
        logger.error(f"Failed to create calculation: {str(e)}")
        raise

@router.get("/", response_model=CalculationListResponse)
async def get_calculations(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Number of records to return"),
    calculation_type: Optional[str] = Query(None, description="Filter by calculation type"),
    status: Optional[str] = Query(None, description="Filter by calculation status"),
    project_id: Optional[int] = Query(None, description="Filter by project ID"),
    vessel_id: Optional[int] = Query(None, description="Filter by vessel ID"),
    search: Optional[str] = Query(None, description="Search in calculation names and descriptions"),
    sort_by: str = Query("created_at", description="Sort field"),
    sort_order: str = Query("desc", regex="^(asc|desc)$", description="Sort order"),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Get paginated list of calculations with filtering and sorting.
    """
    try:
        # Build filter conditions
        filters = []
        
        if calculation_type:
            filters.append(calculation_crud.model.calculation_type == calculation_type)
        
        if status:
            filters.append(calculation_crud.model.status == status)
        
        if project_id:
            filters.append(calculation_crud.model.project_id == project_id)
        
        if vessel_id:
            filters.append(calculation_crud.model.vessel_id == vessel_id)
        
        # Organization-based filtering through projects
        from app.db.models.project import Project
        organization_projects = db.query(Project.id).filter(Project.organization_id == current_user.organization_id).subquery()
        filters.append(calculation_crud.model.project_id.in_(organization_projects))
        
        # Search functionality
        if search:
            search_filter = or_(
                calculation_crud.model.name.ilike(f"%{search}%"),
                calculation_crud.model.description.ilike(f"%{search}%")
            )
            filters.append(search_filter)
        
        # Get calculations with filters
        calculations = calculation_crud.get_multi_filtered(
            db=db,
            skip=skip,
            limit=limit,
            filters=filters,
            sort_by=sort_by,
            sort_order=sort_order
        )
        
        # Get total count for pagination
        total_count = calculation_crud.count_filtered(
            db=db,
            filters=filters
        )
        
        return {
            "items": calculations,
            "total": total_count,
            "page": (skip // limit) + 1,
            "per_page": limit,
            "pages": (total_count + limit - 1) // limit
        }
        
    except Exception as e:
        logger.error(f"Failed to get calculations: {str(e)}")
        raise

@router.get("/{calculation_id}", response_model=CalculationResponse)
async def get_calculation(
    calculation_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Get a specific calculation by ID.
    """
    calculation = calculation_crud.get(db=db, id=calculation_id)
    
    if not calculation:
        raise_not_found("Calculation", calculation_id)
    
    # Check organization access
    if calculation.organization_id != current_user.organization_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to this calculation"
        )
    
    return calculation

@router.put("/{calculation_id}", response_model=CalculationResponse)
async def update_calculation(
    calculation_id: int,
    calculation_data: CalculationUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Update an existing calculation.
    """
    calculation = calculation_crud.get(db=db, id=calculation_id)
    
    if not calculation:
        raise_not_found("Calculation", calculation_id)
    
    # Check organization access
    if calculation.organization_id != current_user.organization_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to this calculation"
        )
    
    # Validate update permissions
    if calculation.status in ["completed", "failed"]:
        raise_business_rule_violation(
            "Cannot update completed or failed calculations",
            rule_name="calculation_status_update"
        )
    
    # Validate parameters if provided
    if calculation_data.input_parameters:
        validation_service = ValidationService()
        validation_result = validation_service.validate_calculation_parameters(
            calculation_data.input_parameters,
            calculation.calculation_type
        )
        
        if not validation_result["valid"]:
            raise_validation_error(
                f"Calculation parameters validation failed: {', '.join(validation_result['errors'])}"
            )
    
    updated_calculation = calculation_crud.update(
        db=db,
        db_obj=calculation,
        obj_in=calculation_data
    )
    
    logger.info(
        f"Calculation updated: {calculation_id} by user {current_user.id}",
        extra={
            "calculation_id": calculation_id,
            "user_id": current_user.id,
            "updated_fields": list(calculation_data.dict(exclude_unset=True).keys())
        }
    )
    
    return updated_calculation

@router.delete("/{calculation_id}")
async def delete_calculation(
    calculation_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Delete a calculation.
    """
    calculation = calculation_crud.get(db=db, id=calculation_id)
    
    if not calculation:
        raise_not_found("Calculation", calculation_id)
    
    # Check organization access
    if calculation.organization_id != current_user.organization_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to this calculation"
        )
    
    # Check if calculation can be deleted
    if calculation.status == "running":
        raise_business_rule_violation(
            "Cannot delete a calculation that is currently running",
            rule_name="calculation_deletion"
        )
    
    calculation_crud.remove(db=db, id=calculation_id)
    
    logger.info(
        f"Calculation deleted: {calculation_id} by user {current_user.id}",
        extra={
            "calculation_id": calculation_id,
            "user_id": current_user.id
        }
    )
    
    return {"message": "Calculation deleted successfully"}

@router.post("/{calculation_id}/execute")
async def execute_calculation(
    calculation_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Execute a calculation immediately.
    """
    calculation = calculation_crud.get(db=db, id=calculation_id)
    
    if not calculation:
        raise_not_found("Calculation", calculation_id)
    
    # Check organization access
    if calculation.organization_id != current_user.organization_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to this calculation"
        )
    
    # Check if calculation can be executed
    if calculation.status in ["running", "completed"]:
        raise_business_rule_violation(
            f"Cannot execute calculation in '{calculation.status}' status",
            rule_name="calculation_execution"
        )
    
    # Execute calculation
    calculation_service = CalculationService()
    result = await calculation_service.execute_calculation(
        calculation_id=calculation_id,
        db=db
    )
    
    logger.info(
        f"Calculation executed: {calculation_id} by user {current_user.id}",
        extra={
            "calculation_id": calculation_id,
            "user_id": current_user.id,
            "execution_result": result.get("status")
        }
    )
    
    return result

@router.get("/{calculation_id}/result", response_model=CalculationResultResponse)
async def get_calculation_result(
    calculation_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Get calculation results and analysis.
    """
    calculation = calculation_crud.get(db=db, id=calculation_id)
    
    if not calculation:
        raise_not_found("Calculation", calculation_id)
    
    # Check organization access
    if calculation.organization_id != current_user.organization_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to this calculation"
        )
    
    # Get calculation result
    result = calculation_crud.get_result(db=db, calculation_id=calculation_id)
    
    if not result:
        raise_not_found("Calculation result", calculation_id)
    
    return result

@router.post("/bulk", response_model=CalculationBulkResponse)
async def create_bulk_calculations(
    bulk_data: CalculationBulkCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Create multiple calculations in bulk.
    """
    try:
        # Validate bulk creation limits
        if len(bulk_data.calculations) > 50:
            raise_validation_error("Cannot create more than 50 calculations at once")
        
        # Check user permissions
        if not current_user.can_perform_calculations:
            raise_business_rule_violation(
                "User does not have permission to perform calculations",
                rule_name="calculation_permission"
            )
        
        # Validate all calculations
        validation_service = ValidationService()
        validation_errors = []
        
        for i, calc_data in enumerate(bulk_data.calculations):
            validation_result = validation_service.validate_calculation_parameters(
                calc_data.input_parameters,
                calc_data.calculation_type
            )
            
            if not validation_result["valid"]:
                validation_errors.append(f"Calculation {i+1}: {', '.join(validation_result['errors'])}")
        
        if validation_errors:
            raise_validation_error(f"Bulk validation failed: {'; '.join(validation_errors)}")
        
        # Create calculations
        created_calculations = []
        for calc_data in bulk_data.calculations:
            calculation = calculation_crud.create(
                db=db,
                obj_in=calc_data,
                user_id=current_user.id
            )
            created_calculations.append(calculation)
        
        logger.info(
            f"Bulk calculations created: {len(created_calculations)} by user {current_user.id}",
            extra={
                "calculation_count": len(created_calculations),
                "user_id": current_user.id
            }
        )
        
        return {
            "created_count": len(created_calculations),
            "calculations": created_calculations
        }
        
    except Exception as e:
        logger.error(f"Failed to create bulk calculations: {str(e)}")
        raise

@router.get("/types/available")
async def get_available_calculation_types():
    """
    Get list of available calculation types with descriptions.
    """
    calculation_types = [
        {
            "type": "ASME_VIII_DIV_1",
            "name": "ASME VIII Div 1 - Pressure Vessels",
            "description": "Design of pressure vessels according to ASME Boiler and Pressure Vessel Code Section VIII Division 1",
            "category": "pressure_vessel",
            "standards": ["ASME VIII Div 1"],
            "applicable_codes": ["ASME"]
        },
        {
            "type": "ASME_VIII_DIV_2",
            "name": "ASME VIII Div 2 - Alternative Rules",
            "description": "Design of pressure vessels using alternative rules from ASME VIII Division 2",
            "category": "pressure_vessel",
            "standards": ["ASME VIII Div 2"],
            "applicable_codes": ["ASME"]
        },
        {
            "type": "ASME_B31_3",
            "name": "ASME B31.3 - Process Piping",
            "description": "Design and analysis of process piping systems",
            "category": "piping",
            "standards": ["ASME B31.3"],
            "applicable_codes": ["ASME"]
        },
        {
            "type": "API_579",
            "name": "API 579 - Fitness for Service",
            "description": "Assessment of existing equipment for continued service",
            "category": "fitness_for_service",
            "standards": ["API 579"],
            "applicable_codes": ["API"]
        },
        {
            "type": "EN_13445",
            "name": "EN 13445 - European Standard",
            "description": "Design of pressure vessels according to European standard EN 13445",
            "category": "pressure_vessel",
            "standards": ["EN 13445"],
            "applicable_codes": ["EN"]
        }
    ]
    
    return {"calculation_types": calculation_types}

@router.get("/stats/summary")
async def get_calculation_stats(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Get calculation statistics and summary.
    """
    try:
        stats = calculation_crud.get_organization_stats(
            db=db,
            organization_id=current_user.organization_id
        )
        
        return stats
        
    except Exception as e:
        logger.error(f"Failed to get calculation stats: {str(e)}")
        raise
