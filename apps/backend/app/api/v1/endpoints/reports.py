"""
Report API endpoints.

Handles report generation, storage, and retrieval for
vessels, calculations, and inspections.
"""

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status, BackgroundTasks
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.api.dependencies import (
    get_current_user,
    get_db,
    require_role,
    get_pagination_params
)
from app.crud import report as report_crud
from app.db.models.user import User
from app.schemas import (
    Report,
    ReportCreate,
    ReportUpdate,
    ReportList,
    ReportSummary,
    ReportStatistics,
    ReportDashboard,
    ReportGenerationRequest,
    ReportDownloadInfo,
    ReportBatchRequest
)

router = APIRouter()


@router.get("/", response_model=ReportList)
def get_reports(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    search: Optional[str] = Query(None, min_length=1),
    report_type: Optional[str] = Query(None),
    format: Optional[str] = Query(None),
    vessel_id: Optional[int] = Query(None),
    project_id: Optional[int] = Query(None),
    status: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get reports in user's organization.
    
    Supports filtering by type, format, vessel, project, status, and search.
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
        
        reports = report_crud.get_by_vessel(
            db, vessel_id=vessel_id, skip=skip, limit=limit
        )
        total = report_crud.get_report_count_by_vessel(db, vessel_id=vessel_id)
    elif project_id:
        # Verify project belongs to user's organization
        from app.crud import project as project_crud
        project = project_crud.get(db, id=project_id)
        if not project or project.organization_id != current_user.organization_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found"
            )
        
        reports = report_crud.get_by_project(
            db, project_id=project_id, skip=skip, limit=limit
        )
        total = len(report_crud.get_by_project(
            db, project_id=project_id, skip=0, limit=10000
        ))
    elif search:
        reports = report_crud.search(
            db, query=search, organization_id=current_user.organization_id, skip=skip, limit=limit
        )
        total = len(report_crud.search(
            db, query=search, organization_id=current_user.organization_id, skip=0, limit=10000
        ))
    elif report_type:
        reports = report_crud.get_by_report_type(
            db, report_type=report_type, organization_id=current_user.organization_id, skip=skip, limit=limit
        )
        total = len(report_crud.get_by_report_type(
            db, report_type=report_type, organization_id=current_user.organization_id, skip=0, limit=10000
        ))
    else:
        # Get all reports for organization
        reports = []
        total = report_crud.get_report_count_by_organization(
            db, organization_id=current_user.organization_id
        )
    
    return ReportList(
        items=reports,
        total=total,
        page=skip // limit + 1,
        per_page=limit,
        pages=(total + limit - 1) // limit
    )


@router.post("/", response_model=Report, status_code=status.HTTP_201_CREATED)
def create_report(
    report_in: ReportCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["engineer", "organization_admin", "super_admin"]))
):
    """
    Create new report and queue for generation.
    
    Engineers and admins can create reports for vessels in their organization.
    """
    if not current_user.organization_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User is not associated with any organization"
        )
    
    # Verify vessel exists and belongs to user's organization
    from app.crud import vessel as vessel_crud
    vessel = vessel_crud.get(db, id=report_in.vessel_id)
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
    
    # Verify calculation if provided
    if report_in.calculation_id:
        from app.crud import calculation as calculation_crud
        calculation = calculation_crud.get(db, id=report_in.calculation_id)
        if not calculation or calculation.vessel_id != report_in.vessel_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Calculation not found or does not belong to specified vessel"
            )
    
    # Verify inspection if provided
    if report_in.inspection_id:
        from app.crud import inspection as inspection_crud
        inspection = inspection_crud.get(db, id=report_in.inspection_id)
        if not inspection or inspection.vessel_id != report_in.vessel_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Inspection not found or does not belong to specified vessel"
            )
    
    # Create report data
    report_data = report_in.dict()
    report_data.update({
        "created_by_id": current_user.id,
        "status": "pending"
    })
    
    report = report_crud.create(db, obj_in=report_data)
    
    # Queue report generation in background
    background_tasks.add_task(generate_report_background, report.id, db)
    
    return report


@router.post("/generate", response_model=Report, status_code=status.HTTP_201_CREATED)
def generate_report(
    request: ReportGenerationRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["engineer", "organization_admin", "super_admin"]))
):
    """
    Generate report using simplified request format.
    """
    if not current_user.organization_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User is not associated with any organization"
        )
    
    # Verify vessel exists and belongs to user's organization
    from app.crud import vessel as vessel_crud
    vessel = vessel_crud.get(db, id=request.vessel_id)
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
    
    # Create report
    report_data = {
        "name": f"{request.report_type} - {vessel.tag_number}",
        "description": f"Auto-generated {request.report_type} report",
        "report_type": request.report_type,
        "format": request.format,
        "vessel_id": request.vessel_id,
        "template_id": request.template_id,
        "parameters": request.parameters,
        "created_by_id": current_user.id,
        "status": "pending"
    }
    
    report = report_crud.create(db, obj_in=report_data)
    
    # Queue report generation in background
    background_tasks.add_task(generate_report_background, report.id, db)
    
    return report


@router.post("/batch", response_model=List[Report], status_code=status.HTTP_201_CREATED)
def generate_batch_reports(
    request: ReportBatchRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["engineer", "organization_admin", "super_admin"]))
):
    """
    Generate reports for multiple vessels.
    """
    if not current_user.organization_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User is not associated with any organization"
        )
    
    # Verify all vessels exist and belong to user's organization
    from app.crud import vessel as vessel_crud
    vessels = []
    for vessel_id in request.vessel_ids:
        vessel = vessel_crud.get(db, id=vessel_id)
        if not vessel:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Vessel {vessel_id} not found"
            )
        
        if vessel.organization_id != current_user.organization_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Vessel {vessel_id} does not belong to your organization"
            )
        
        vessels.append(vessel)
    
    # Create reports for each vessel
    reports = []
    for vessel in vessels:
        report_data = {
            "name": f"{request.report_type} - {vessel.tag_number}",
            "description": f"Batch generated {request.report_type} report",
            "report_type": request.report_type,
            "format": request.format,
            "vessel_id": vessel.id,
            "template_id": request.template_id,
            "parameters": request.parameters,
            "created_by_id": current_user.id,
            "status": "pending"
        }
        
        report = report_crud.create(db, obj_in=report_data)
        reports.append(report)
        
        # Queue report generation in background
        background_tasks.add_task(generate_report_background, report.id, db)
    
    return reports


@router.get("/dashboard", response_model=ReportDashboard)
def get_report_dashboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get report dashboard data for user's organization.
    """
    if not current_user.organization_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User is not associated with any organization"
        )
    
    # Get recent reports
    recent_reports = report_crud.get_recent_reports(
        db, organization_id=current_user.organization_id, days=30, limit=5
    )
    
    # Get pending reports
    pending_reports = report_crud.get_pending_reports(
        db, organization_id=current_user.organization_id, skip=0, limit=5
    )
    
    # Get failed reports
    failed_reports = report_crud.get_failed_reports(
        db, organization_id=current_user.organization_id, skip=0, limit=5
    )
    
    # Get downloadable reports
    downloadable_reports = report_crud.get_downloadable_reports(
        db, organization_id=current_user.organization_id, skip=0, limit=5
    )
    
    # Get statistics
    statistics = report_crud.get_report_statistics(
        db, organization_id=current_user.organization_id
    )
    
    return ReportDashboard(
        recent_reports=[ReportSummary.from_orm(r) for r in recent_reports],
        pending_reports=[ReportSummary.from_orm(r) for r in pending_reports],
        failed_reports=[ReportSummary.from_orm(r) for r in failed_reports],
        downloadable_reports=[ReportSummary.from_orm(r) for r in downloadable_reports],
        statistics=ReportStatistics(**statistics)
    )


@router.get("/statistics", response_model=ReportStatistics)
def get_report_statistics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get report statistics for user's organization.
    """
    if not current_user.organization_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User is not associated with any organization"
        )
    
    statistics = report_crud.get_report_statistics(
        db, organization_id=current_user.organization_id
    )
    
    return ReportStatistics(**statistics)


@router.get("/downloadable", response_model=List[ReportSummary])
def get_downloadable_reports(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=1000),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get completed reports that can be downloaded.
    """
    if not current_user.organization_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User is not associated with any organization"
        )
    
    reports = report_crud.get_downloadable_reports(
        db, organization_id=current_user.organization_id, skip=skip, limit=limit
    )
    
    return [ReportSummary.from_orm(r) for r in reports]


@router.get("/pending", response_model=List[ReportSummary])
def get_pending_reports(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=1000),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get reports that are still being generated.
    """
    if not current_user.organization_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User is not associated with any organization"
        )
    
    reports = report_crud.get_pending_reports(
        db, organization_id=current_user.organization_id, skip=skip, limit=limit
    )
    
    return [ReportSummary.from_orm(r) for r in reports]


@router.get("/failed", response_model=List[ReportSummary])
def get_failed_reports(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=1000),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get failed reports that need attention.
    """
    if not current_user.organization_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User is not associated with any organization"
        )
    
    reports = report_crud.get_failed_reports(
        db, organization_id=current_user.organization_id, skip=skip, limit=limit
    )
    
    return [ReportSummary.from_orm(r) for r in reports]


@router.get("/{report_id}", response_model=Report)
def get_report(
    report_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get report by ID.
    
    Users can only access reports for vessels in their organization.
    """
    report = report_crud.get(db, id=report_id)
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report not found"
        )
    
    # Check permissions through vessel
    from app.crud import vessel as vessel_crud
    vessel = vessel_crud.get(db, id=report.vessel_id)
    if not vessel:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Associated vessel not found"
        )
    
    if (current_user.role != "super_admin" and 
        vessel.organization_id != current_user.organization_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to access this report"
        )
    
    return report


@router.get("/{report_id}/download", response_class=FileResponse)
def download_report(
    report_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Download report file.
    """
    report = report_crud.get(db, id=report_id)
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report not found"
        )
    
    # Check permissions through vessel
    from app.crud import vessel as vessel_crud
    vessel = vessel_crud.get(db, id=report.vessel_id)
    if not vessel:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Associated vessel not found"
        )
    
    if (current_user.role != "super_admin" and 
        vessel.organization_id != current_user.organization_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to download this report"
        )
    
    if report.status != "completed" or not report.file_path:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Report is not ready for download"
        )
    
    # Check if file exists
    import os
    if not os.path.exists(report.file_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report file not found"
        )
    
    # Determine content type based on format
    content_type_map = {
        "pdf": "application/pdf",
        "docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        "html": "text/html",
        "csv": "text/csv"
    }
    
    content_type = content_type_map.get(report.format, "application/octet-stream")
    filename = f"{report.name}.{report.format}"
    
    return FileResponse(
        path=report.file_path,
        media_type=content_type,
        filename=filename
    )


@router.put("/{report_id}", response_model=Report)
def update_report(
    report_id: int,
    report_in: ReportUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["engineer", "organization_admin", "super_admin"]))
):
    """
    Update report.
    
    Engineers and admins can update reports for vessels in their organization.
    """
    report = report_crud.get(db, id=report_id)
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report not found"
        )
    
    # Check permissions through vessel
    from app.crud import vessel as vessel_crud
    vessel = vessel_crud.get(db, id=report.vessel_id)
    if not vessel:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Associated vessel not found"
        )
    
    if (current_user.role != "super_admin" and 
        vessel.organization_id != current_user.organization_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to update this report"
        )
    
    # Update report
    update_data = report_in.dict(exclude_unset=True)
    report = report_crud.update(db, db_obj=report, obj_in=update_data)
    return report


@router.delete("/{report_id}", response_model=Report)
def deactivate_report(
    report_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["organization_admin", "super_admin"]))
):
    """
    Deactivate report (soft delete).
    
    Only organization admins and super admins can deactivate reports.
    """
    report = report_crud.get(db, id=report_id)
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report not found"
        )
    
    # Check permissions through vessel
    from app.crud import vessel as vessel_crud
    vessel = vessel_crud.get(db, id=report.vessel_id)
    if not vessel:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Associated vessel not found"
        )
    
    if (current_user.role != "super_admin" and 
        vessel.organization_id != current_user.organization_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to deactivate this report"
        )
    
    report = report_crud.soft_delete(db, id=report_id)
    return report


@router.get("/types/available", response_model=List[str])
def get_available_report_types():
    """
    Get available report types.
    """
    return [
        "vessel_datasheet", "calculation_report", "inspection_report",
        "compliance_report", "design_report", "stress_analysis",
        "material_certificate", "pressure_test", "project_summary", "other"
    ]


@router.get("/formats/available", response_model=List[str])
def get_available_formats():
    """
    Get available report formats.
    """
    return ["pdf", "docx", "xlsx", "html", "csv"]


# Background task for report generation
def generate_report_background(report_id: int, db: Session):
    """
    Background task to generate report.
    
    This is a placeholder that would integrate with actual report generation services.
    """
    try:
        # Update status to generating
        report_crud.update_status(db, report_id=report_id, status="generating")
        
        # Here you would implement actual report generation logic
        # For now, we'll simulate successful generation
        import time
        time.sleep(2)  # Simulate processing time
        
        # Simulate file creation
        import tempfile
        import os
        
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
        temp_file.write(b"Sample report content")
        temp_file.close()
        
        file_size = os.path.getsize(temp_file.name)
        
        # Update status to completed
        report_crud.update_status(
            db,
            report_id=report_id,
            status="completed",
            file_path=temp_file.name,
            file_size=file_size
        )
        
    except Exception as e:
        # Update status to failed
        report_crud.update_status(
            db,
            report_id=report_id,
            status="failed",
            error_message=str(e)
        )
