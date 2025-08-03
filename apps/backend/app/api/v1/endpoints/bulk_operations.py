"""
Bulk operations endpoints for efficient data management.

Provides batch processing capabilities for common operations
to reduce API calls and improve performance.
"""

from typing import List, Dict, Any, Optional, Union
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field, validator

from app.api.dependencies import get_current_user, get_db, require_role
from app.db.models.user import User, UserRole
from app.services.audit_service import audit_service, AuditEventType, AuditSeverity, AuditContext
from app.crud import project as project_crud, vessel as vessel_crud, calculation as calculation_crud
from app.schemas.project import ProjectCreate, ProjectUpdate, Project
from app.schemas.vessel import VesselCreate, VesselUpdate, Vessel
from app.schemas.calculation import CalculationCreate, CalculationUpdate, Calculation
from app.core.logging_config import get_logger
from app.utils.error_handling import VesselGuardException, ErrorCode

logger = get_logger(__name__)
router = APIRouter()


class BulkOperationResult(BaseModel):
    """Result of a bulk operation."""
    success_count: int = Field(..., ge=0)
    error_count: int = Field(..., ge=0)
    total_count: int = Field(..., ge=0)
    success_ids: List[int] = Field(default_factory=list)
    errors: List[Dict[str, Any]] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)


class BulkProjectCreate(BaseModel):
    """Bulk project creation request."""
    projects: List[ProjectCreate] = Field(..., min_items=1, max_items=100)
    skip_duplicates: bool = Field(default=False, description="Skip projects that already exist")
    continue_on_error: bool = Field(default=True, description="Continue processing if individual items fail")

    @validator('projects')
    def validate_projects(cls, v):
        if len(v) > 100:
            raise ValueError("Maximum 100 projects allowed per bulk operation")
        return v


class BulkProjectUpdate(BaseModel):
    """Bulk project update request."""
    updates: List[Dict[str, Any]] = Field(..., min_items=1, max_items=100)
    project_ids: List[int] = Field(..., min_items=1, max_items=100)
    skip_missing: bool = Field(default=False, description="Skip projects that don't exist")

    @validator('project_ids', 'updates')
    def validate_lengths_match(cls, v, values):
        if 'updates' in values and len(v) != len(values['updates']):
            raise ValueError("project_ids and updates must have the same length")
        return v


class BulkVesselCreate(BaseModel):
    """Bulk vessel creation request."""
    vessels: List[VesselCreate] = Field(..., min_items=1, max_items=50)
    project_id: int = Field(..., description="Project ID for all vessels")
    skip_duplicates: bool = Field(default=False)
    continue_on_error: bool = Field(default=True)


class BulkCalculationCreate(BaseModel):
    """Bulk calculation creation request."""
    calculations: List[CalculationCreate] = Field(..., min_items=1, max_items=50)
    continue_on_error: bool = Field(default=True)


class BulkDeleteRequest(BaseModel):
    """Bulk delete request."""
    ids: List[int] = Field(..., min_items=1, max_items=100)
    hard_delete: bool = Field(default=False, description="Permanently delete instead of soft delete")
    force: bool = Field(default=False, description="Force delete even if dependencies exist")


@router.post("/projects/create", response_model=BulkOperationResult)
async def bulk_create_projects(
    bulk_request: BulkProjectCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role([UserRole.ENGINEER]))
):
    """
    Create multiple projects in a single operation.
    
    Efficiently creates multiple projects with proper error handling
    and transaction management.
    """
    try:
        success_count = 0
        error_count = 0
        success_ids = []
        errors = []
        warnings = []
        
        # Audit context
        audit_context = AuditContext(
            user_id=current_user.id,
            organization_id=current_user.organization_id,
            api_endpoint="/api/v1/bulk/projects/create",
            http_method="POST"
        )
        
        # Process each project
        for i, project_data in enumerate(bulk_request.projects):
            try:
                # Set organization ID
                project_data.organization_id = current_user.organization_id
                
                # Check for duplicates if requested
                if bulk_request.skip_duplicates:
                    existing = project_crud.get_by_name_and_organization(
                        db, name=project_data.name, organization_id=current_user.organization_id
                    )
                    if existing:
                        warnings.append(f"Project '{project_data.name}' already exists, skipping")
                        continue
                
                # Create project
                project = project_crud.create(db=db, obj_in=project_data)
                success_count += 1
                success_ids.append(project.id)
                
                logger.info(f"Bulk created project: {project.id}")
                
            except Exception as e:
                error_count += 1
                error_detail = {
                    "index": i,
                    "project_name": getattr(project_data, 'name', f'Project {i+1}'),
                    "error": str(e),
                    "error_type": type(e).__name__
                }
                errors.append(error_detail)
                
                logger.error(f"Failed to create project {i}: {e}")
                
                # Stop on first error if continue_on_error is False
                if not bulk_request.continue_on_error:
                    break
        
        # Commit transaction
        db.commit()
        
        # Log bulk operation
        audit_service.log_event(
            db=db,
            event_type=AuditEventType.BULK_OPERATION,
            description=f"Bulk created {success_count} projects",
            context=audit_context,
            severity=AuditSeverity.MEDIUM,
            details={
                "operation": "bulk_create_projects",
                "total_requested": len(bulk_request.projects),
                "successful": success_count,
                "failed": error_count,
                "success_ids": success_ids
            }
        )
        
        result = BulkOperationResult(
            success_count=success_count,
            error_count=error_count,
            total_count=len(bulk_request.projects),
            success_ids=success_ids,
            errors=errors,
            warnings=warnings
        )
        
        return result
        
    except Exception as e:
        db.rollback()
        logger.error(f"Bulk project creation failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Bulk operation failed: {str(e)}"
        )


@router.patch("/projects/update", response_model=BulkOperationResult)
async def bulk_update_projects(
    bulk_request: BulkProjectUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role([UserRole.ENGINEER]))
):
    """
    Update multiple projects in a single operation.
    """
    try:
        success_count = 0
        error_count = 0
        success_ids = []
        errors = []
        warnings = []
        
        # Process each update
        for i, (project_id, update_data) in enumerate(zip(bulk_request.project_ids, bulk_request.updates)):
            try:
                # Get project
                project = project_crud.get(db=db, id=project_id)
                
                if not project:
                    if bulk_request.skip_missing:
                        warnings.append(f"Project {project_id} not found, skipping")
                        continue
                    else:
                        raise HTTPException(
                            status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Project {project_id} not found"
                        )
                
                # Check permissions
                if project.organization_id != current_user.organization_id:
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail=f"Not authorized to update project {project_id}"
                    )
                
                # Create update object
                project_update = ProjectUpdate(**update_data)
                
                # Update project
                updated_project = project_crud.update(db=db, db_obj=project, obj_in=project_update)
                success_count += 1
                success_ids.append(updated_project.id)
                
                logger.info(f"Bulk updated project: {updated_project.id}")
                
            except Exception as e:
                error_count += 1
                error_detail = {
                    "index": i,
                    "project_id": project_id,
                    "error": str(e),
                    "error_type": type(e).__name__
                }
                errors.append(error_detail)
                
                logger.error(f"Failed to update project {project_id}: {e}")
        
        # Commit transaction
        db.commit()
        
        # Log bulk operation
        audit_context = AuditContext(
            user_id=current_user.id,
            organization_id=current_user.organization_id,
            api_endpoint="/api/v1/bulk/projects/update",
            http_method="PATCH"
        )
        
        audit_service.log_event(
            db=db,
            event_type=AuditEventType.BULK_OPERATION,
            description=f"Bulk updated {success_count} projects",
            context=audit_context,
            severity=AuditSeverity.MEDIUM,
            details={
                "operation": "bulk_update_projects",
                "total_requested": len(bulk_request.project_ids),
                "successful": success_count,
                "failed": error_count,
                "success_ids": success_ids
            }
        )
        
        return BulkOperationResult(
            success_count=success_count,
            error_count=error_count,
            total_count=len(bulk_request.project_ids),
            success_ids=success_ids,
            errors=errors,
            warnings=warnings
        )
        
    except Exception as e:
        db.rollback()
        logger.error(f"Bulk project update failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Bulk operation failed: {str(e)}"
        )


@router.delete("/projects", response_model=BulkOperationResult)
async def bulk_delete_projects(
    bulk_request: BulkDeleteRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role([UserRole.ENGINEER]))
):
    """
    Delete multiple projects in a single operation.
    """
    try:
        success_count = 0
        error_count = 0
        success_ids = []
        errors = []
        warnings = []
        
        # Check if user has permission for hard deletes
        if bulk_request.hard_delete and current_user.role != UserRole.ENGINEER:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Hard delete requires engineer role"
            )
        
        # Process each delete
        for project_id in bulk_request.ids:
            try:
                # Get project
                project = project_crud.get(db=db, id=project_id)
                
                if not project:
                    warnings.append(f"Project {project_id} not found, skipping")
                    continue
                
                # Check permissions
                if project.organization_id != current_user.organization_id:
                    error_count += 1
                    errors.append({
                        "project_id": project_id,
                        "error": "Not authorized to delete this project",
                        "error_type": "AuthorizationError"
                    })
                    continue
                
                # Check dependencies if not forcing
                if not bulk_request.force:
                    # Check if project has vessels
                    vessels = vessel_crud.get_by_project(db=db, project_id=project_id)
                    if vessels:
                        error_count += 1
                        errors.append({
                            "project_id": project_id,
                            "error": f"Project has {len(vessels)} vessels. Use force=true to delete anyway.",
                            "error_type": "DependencyError"
                        })
                        continue
                
                # Delete project
                if bulk_request.hard_delete:
                    # Hard delete - remove from database
                    db.delete(project)
                else:
                    # Soft delete - mark as inactive
                    project.is_active = False
                    db.commit()
                
                success_count += 1
                success_ids.append(project_id)
                
                logger.info(f"Bulk deleted project: {project_id} (hard={bulk_request.hard_delete})")
                
            except Exception as e:
                error_count += 1
                errors.append({
                    "project_id": project_id,
                    "error": str(e),
                    "error_type": type(e).__name__
                })
                
                logger.error(f"Failed to delete project {project_id}: {e}")
        
        # Commit transaction
        db.commit()
        
        # Log bulk operation
        audit_context = AuditContext(
            user_id=current_user.id,
            organization_id=current_user.organization_id,
            api_endpoint="/api/v1/bulk/projects",
            http_method="DELETE"
        )
        
        audit_service.log_event(
            db=db,
            event_type=AuditEventType.BULK_OPERATION,
            description=f"Bulk deleted {success_count} projects",
            context=audit_context,
            severity=AuditSeverity.HIGH if bulk_request.hard_delete else AuditSeverity.MEDIUM,
            details={
                "operation": "bulk_delete_projects",
                "total_requested": len(bulk_request.ids),
                "successful": success_count,
                "failed": error_count,
                "hard_delete": bulk_request.hard_delete,
                "success_ids": success_ids
            },
            is_sensitive=bulk_request.hard_delete
        )
        
        return BulkOperationResult(
            success_count=success_count,
            error_count=error_count,
            total_count=len(bulk_request.ids),
            success_ids=success_ids,
            errors=errors,
            warnings=warnings
        )
        
    except Exception as e:
        db.rollback()
        logger.error(f"Bulk project deletion failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Bulk operation failed: {str(e)}"
        )


@router.post("/vessels/create", response_model=BulkOperationResult)
async def bulk_create_vessels(
    bulk_request: BulkVesselCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role([UserRole.ENGINEER]))
):
    """
    Create multiple vessels for a project in a single operation.
    """
    try:
        # Verify project exists and user has access
        project = project_crud.get(db=db, id=bulk_request.project_id)
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found"
            )
        
        if project.organization_id != current_user.organization_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to access this project"
            )
        
        success_count = 0
        error_count = 0
        success_ids = []
        errors = []
        warnings = []
        
        # Process each vessel
        for i, vessel_data in enumerate(bulk_request.vessels):
            try:
                # Set project ID
                vessel_data.project_id = bulk_request.project_id
                
                # Check for duplicates if requested
                if bulk_request.skip_duplicates:
                    existing = vessel_crud.get_by_tag_and_project(
                        db, tag_number=vessel_data.tag_number, project_id=bulk_request.project_id
                    )
                    if existing:
                        warnings.append(f"Vessel '{vessel_data.tag_number}' already exists, skipping")
                        continue
                
                # Create vessel
                vessel = vessel_crud.create(db=db, obj_in=vessel_data)
                success_count += 1
                success_ids.append(vessel.id)
                
                logger.info(f"Bulk created vessel: {vessel.id}")
                
            except Exception as e:
                error_count += 1
                error_detail = {
                    "index": i,
                    "vessel_tag": getattr(vessel_data, 'tag_number', f'Vessel {i+1}'),
                    "error": str(e),
                    "error_type": type(e).__name__
                }
                errors.append(error_detail)
                
                logger.error(f"Failed to create vessel {i}: {e}")
                
                if not bulk_request.continue_on_error:
                    break
        
        # Commit transaction
        db.commit()
        
        # Log bulk operation
        audit_context = AuditContext(
            user_id=current_user.id,
            organization_id=current_user.organization_id,
            api_endpoint="/api/v1/bulk/vessels/create",
            http_method="POST"
        )
        
        audit_service.log_event(
            db=db,
            event_type=AuditEventType.BULK_OPERATION,
            description=f"Bulk created {success_count} vessels for project {bulk_request.project_id}",
            context=audit_context,
            severity=AuditSeverity.MEDIUM,
            details={
                "operation": "bulk_create_vessels",
                "project_id": bulk_request.project_id,
                "total_requested": len(bulk_request.vessels),
                "successful": success_count,
                "failed": error_count,
                "success_ids": success_ids
            }
        )
        
        return BulkOperationResult(
            success_count=success_count,
            error_count=error_count,
            total_count=len(bulk_request.vessels),
            success_ids=success_ids,
            errors=errors,
            warnings=warnings
        )
        
    except Exception as e:
        db.rollback()
        logger.error(f"Bulk vessel creation failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Bulk operation failed: {str(e)}"
        )


@router.post("/calculations/create", response_model=BulkOperationResult)
async def bulk_create_calculations(
    bulk_request: BulkCalculationCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role([UserRole.ENGINEER]))
):
    """
    Create multiple calculations in a single operation.
    
    Calculations will be processed in the background for better performance.
    """
    try:
        success_count = 0
        error_count = 0
        success_ids = []
        errors = []
        warnings = []
        
        # Process each calculation
        for i, calc_data in enumerate(bulk_request.calculations):
            try:
                # Validate calculation access
                if calc_data.vessel_id:
                    vessel = vessel_crud.get(db=db, id=calc_data.vessel_id)
                    if vessel and vessel.project.organization_id != current_user.organization_id:
                        raise HTTPException(
                            status_code=status.HTTP_403_FORBIDDEN,
                            detail=f"Not authorized to access vessel {calc_data.vessel_id}"
                        )
                
                # Create calculation
                calculation = calculation_crud.create(
                    db=db, 
                    obj_in=calc_data, 
                    user_id=current_user.id
                )
                success_count += 1
                success_ids.append(calculation.id)
                
                logger.info(f"Bulk created calculation: {calculation.id}")
                
            except Exception as e:
                error_count += 1
                error_detail = {
                    "index": i,
                    "calculation_type": getattr(calc_data, 'calculation_type', 'unknown'),
                    "error": str(e),
                    "error_type": type(e).__name__
                }
                errors.append(error_detail)
                
                logger.error(f"Failed to create calculation {i}: {e}")
                
                if not bulk_request.continue_on_error:
                    break
        
        # Commit transaction
        db.commit()
        
        # Log bulk operation
        audit_context = AuditContext(
            user_id=current_user.id,
            organization_id=current_user.organization_id,
            api_endpoint="/api/v1/bulk/calculations/create",
            http_method="POST"
        )
        
        audit_service.log_event(
            db=db,
            event_type=AuditEventType.BULK_OPERATION,
            description=f"Bulk created {success_count} calculations",
            context=audit_context,
            severity=AuditSeverity.MEDIUM,
            details={
                "operation": "bulk_create_calculations",
                "total_requested": len(bulk_request.calculations),
                "successful": success_count,
                "failed": error_count,
                "success_ids": success_ids
            }
        )
        
        return BulkOperationResult(
            success_count=success_count,
            error_count=error_count,
            total_count=len(bulk_request.calculations),
            success_ids=success_ids,
            errors=errors,
            warnings=warnings
        )
        
    except Exception as e:
        db.rollback()
        logger.error(f"Bulk calculation creation failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Bulk operation failed: {str(e)}"
        )


@router.get("/status/{operation_id}")
async def get_bulk_operation_status(
    operation_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get the status of a bulk operation.
    
    For operations that run in the background.
    """
    from celery import current_app as celery_app
    from app.services.background_tasks import background_task_service
    
    try:
        # Check if operation_id is a valid Celery task ID
        if not operation_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Operation ID is required"
            )
        
        # Get task result from Celery
        task_result = celery_app.AsyncResult(operation_id)
        
        # Map Celery states to our status format
        celery_to_status = {
            'PENDING': 'pending',
            'STARTED': 'running',
            'SUCCESS': 'completed',
            'FAILURE': 'failed',
            'RETRY': 'running',
            'REVOKED': 'cancelled'
        }
        
        operation_status = celery_to_status.get(task_result.state, 'unknown')
        
        response = {
            "operation_id": operation_id,
            "status": operation_status,
            "state": task_result.state,
            "current": getattr(task_result.info, 'current', 0) if isinstance(task_result.info, dict) else 0,
            "total": getattr(task_result.info, 'total', 0) if isinstance(task_result.info, dict) else 0,
            "message": "Operation in progress"
        }
        
        # Add specific information based on task state
        if task_result.state == 'PENDING':
            response.update({
                "message": "Task is waiting to be processed",
                "progress_percent": 0
            })
            
        elif task_result.state == 'STARTED':
            response.update({
                "message": "Task is currently running",
                "progress_percent": 0
            })
            
        elif task_result.state == 'SUCCESS':
            result = task_result.result or {}
            response.update({
                "message": "Bulk operation completed successfully",
                "progress_percent": 100,
                "result": {
                    "total_processed": result.get('total_processed', 0),
                    "successful": result.get('successful', 0),
                    "failed": result.get('failed', 0),
                    "errors": result.get('errors', [])
                },
                "completed_at": result.get('completed_at'),
                "duration_seconds": result.get('duration_seconds', 0)
            })
            
        elif task_result.state == 'FAILURE':
            error_info = str(task_result.info) if task_result.info else "Unknown error occurred"
            response.update({
                "message": f"Bulk operation failed: {error_info}",
                "progress_percent": 0,
                "error": error_info,
                "failed_at": getattr(task_result.info, 'failed_at', None) if isinstance(task_result.info, dict) else None
            })
            
        elif task_result.state in ['RETRY', 'PROGRESS']:
            # Handle progress updates
            if isinstance(task_result.info, dict):
                current = task_result.info.get('current', 0)
                total = task_result.info.get('total', 1)
                progress_percent = int((current / total) * 100) if total > 0 else 0
                
                response.update({
                    "message": task_result.info.get('status', 'Processing...'),
                    "progress_percent": progress_percent,
                    "current": current,
                    "total": total,
                    "eta_seconds": task_result.info.get('eta_seconds'),
                    "processing_rate": task_result.info.get('processing_rate', 0)
                })
            else:
                response.update({
                    "message": "Processing bulk operation...",
                    "progress_percent": 0
                })
                
        elif task_result.state == 'REVOKED':
            response.update({
                "message": "Bulk operation was cancelled",
                "progress_percent": 0,
                "cancelled_at": getattr(task_result.info, 'cancelled_at', None) if isinstance(task_result.info, dict) else None
            })
            
        else:
            response.update({
                "message": f"Unknown task state: {task_result.state}",
                "progress_percent": 0
            })
        
        return response
        
    except Exception as e:
        # If Celery is not available or task ID is invalid, check local storage
        try:
            # Try to get status from a simple in-memory store (for development)
            # In production, this should be Redis or database
            status_info = background_task_service.get_operation_status(operation_id)
            
            if status_info:
                return {
                    "operation_id": operation_id,
                    "status": status_info.get('status', 'unknown'),
                    "message": status_info.get('message', 'Operation status retrieved'),
                    "progress_percent": status_info.get('progress_percent', 0),
                    "started_at": status_info.get('started_at'),
                    "updated_at": status_info.get('updated_at'),
                    "result": status_info.get('result')
                }
            else:
                # Operation not found
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Bulk operation with ID '{operation_id}' not found"
                )
                
        except Exception as fallback_error:
            # Final fallback - return error response
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Unable to retrieve operation status: {str(e)}"
            )