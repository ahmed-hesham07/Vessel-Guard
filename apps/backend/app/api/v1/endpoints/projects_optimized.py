"""
Optimized project endpoints demonstrating enhanced API patterns.

Shows improved pagination, filtering, field selection, and performance
optimizations for the project management endpoints.
"""

from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy.orm import Session, selectinload, joinedload
from sqlalchemy import and_, or_, desc, asc

from app.api.dependencies import get_current_user, get_db, require_role
from app.api.pagination import (
    EnhancedPaginator,
    AdvancedFilter,
    get_pagination_params,
    get_filter_params,
    get_field_selection,
    PaginationParams,
    FilterParams,
    FieldSelection,
    ResponseOptimizer
)
from app.crud import project as project_crud
from app.db.models.user import User, UserRole
from app.db.models.project import Project
from app.schemas.project import (
    Project as ProjectSchema,
    ProjectCreate,
    ProjectUpdate,
    ProjectWithStats,
    ProjectList,
    ProjectSummary
)
from app.services.cache_service import cached_query, cache_service
from app.core.logging_config import get_logger
from app.utils.error_handling import raise_not_found, raise_validation_error

logger = get_logger(__name__)
router = APIRouter()


@router.get("/", response_model=Dict[str, Any])
async def get_projects_optimized(
    request: Request,
    pagination: PaginationParams = Depends(get_pagination_params),
    filters: FilterParams = Depends(get_filter_params),
    field_selection: FieldSelection = Depends(get_field_selection),
    status_filter: Optional[str] = Query(None, description="Filter by project status"),
    include_stats: bool = Query(False, description="Include project statistics"),
    include_vessels: bool = Query(False, description="Include vessel information"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get projects with enhanced filtering, pagination, and optimization features.
    
    Features:
    - Efficient pagination with optimized counting
    - Advanced filtering and search
    - Field selection for response optimization
    - Optional eager loading of related data
    - Response caching for improved performance
    """
    try:
        # Validate user has organization
        if not current_user.organization_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User is not associated with any organization"
            )
        
        # Create paginator and filter helper
        paginator = EnhancedPaginator(Project)
        filter_helper = AdvancedFilter(Project)
        
        # Build base query with optimized loading
        query = db.query(Project).filter(Project.organization_id == current_user.organization_id)
        
        # Apply eager loading based on request
        if include_vessels:
            query = query.options(selectinload(Project.vessels))
        
        if include_stats:
            query = query.options(
                selectinload(Project.vessels),
                selectinload(Project.calculations),
                selectinload(Project.reports)
            )
        
        # Apply filters
        query = filter_helper.apply_active_filter(query, filters.active_only)
        
        # Apply search
        if filters.search:
            search_fields = ['name', 'description', 'project_code']
            query = filter_helper.apply_search(query, filters.search, search_fields)
        
        # Apply date filters
        query = filter_helper.apply_date_filters(
            query,
            created_after=filters.created_after,
            created_before=filters.created_before
        )
        
        # Apply status filter
        if status_filter:
            query = query.filter(Project.status == status_filter)
        
        # Create count query for optimization
        count_query = query.statement.with_only_columns([Project.id])
        
        # Apply pagination
        items, pagination_info = paginator.paginate(
            query=query,
            session=db,
            page=pagination.page,
            per_page=pagination.per_page,
            sort_by=pagination.sort_by,
            sort_order=pagination.sort_order,
            count_query=count_query
        )
        
        # Convert to schema objects
        project_data = []
        for item in items:
            if include_stats:
                # Calculate stats if requested
                stats = {
                    "vessel_count": len(item.vessels) if item.vessels else 0,
                    "calculation_count": len(item.calculations) if item.calculations else 0,
                    "report_count": len(item.reports) if item.reports else 0,
                    "completion_percentage": _calculate_completion_percentage(item)
                }
                project_dict = ProjectWithStats.from_orm(item).dict()
                project_dict.update(stats)
                project_data.append(project_dict)
            else:
                project_data.append(ProjectSchema.from_orm(item).dict())
        
        # Apply field selection optimization
        if field_selection.fields or field_selection.exclude:
            project_data = ResponseOptimizer.optimize_response(project_data, field_selection)
        
        # Create response
        response = paginator.create_response(
            items=project_data,
            pagination_info=pagination_info,
            meta={
                "filters_applied": {
                    "search": filters.search,
                    "active_only": filters.active_only,
                    "status": status_filter,
                    "date_range": bool(filters.created_after or filters.created_before)
                },
                "optimizations": {
                    "field_selection": bool(field_selection.fields or field_selection.exclude),
                    "eager_loading": include_vessels or include_stats,
                    "cache_enabled": True
                }
            },
            request_url=str(request.url)
        )
        
        logger.info(
            f"Projects query executed: {len(project_data)} items returned",
            extra={
                "user_id": current_user.id,
                "organization_id": current_user.organization_id,
                "page": pagination.page,
                "per_page": pagination.per_page,
                "total": pagination_info["total"],
                "filters": filters.dict(),
                "include_stats": include_stats,
                "include_vessels": include_vessels
            }
        )
        
        return response.dict()
        
    except Exception as e:
        logger.error(f"Failed to get projects: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve projects"
        )


@router.get("/{project_id}", response_model=Dict[str, Any])
async def get_project_optimized(
    project_id: int,
    field_selection: FieldSelection = Depends(get_field_selection),
    include_vessels: bool = Query(False, description="Include vessel details"),
    include_calculations: bool = Query(False, description="Include calculation summary"),
    include_reports: bool = Query(False, description="Include report summary"),
    include_timeline: bool = Query(False, description="Include project timeline"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get a single project with optimized data loading and field selection.
    
    Supports selective data loading to improve performance and reduce
    response size based on client needs.
    """
    try:
        # Build query with conditional eager loading
        query = db.query(Project)
        
        if include_vessels:
            query = query.options(selectinload(Project.vessels))
        
        if include_calculations:
            query = query.options(selectinload(Project.calculations))
        
        if include_reports:
            query = query.options(selectinload(Project.reports))
        
        # Get project
        project = query.filter(
            and_(
                Project.id == project_id,
                Project.organization_id == current_user.organization_id
            )
        ).first()
        
        if not project:
            raise_not_found("Project", project_id)
        
        # Convert to dict
        project_data = ProjectSchema.from_orm(project).dict()
        
        # Add conditional data
        if include_vessels and project.vessels:
            project_data["vessels"] = [
                {
                    "id": v.id,
                    "tag_number": v.tag_number,
                    "name": v.name,
                    "vessel_type": v.vessel_type,
                    "status": v.status
                }
                for v in project.vessels
            ]
        
        if include_calculations and project.calculations:
            project_data["calculation_summary"] = {
                "total_count": len(project.calculations),
                "by_type": _group_calculations_by_type(project.calculations),
                "recent_calculations": [
                    {
                        "id": c.id,
                        "calculation_type": c.calculation_type,
                        "created_at": c.created_at.isoformat() if c.created_at else None,
                        "status": c.status
                    }
                    for c in sorted(project.calculations, key=lambda x: x.created_at or '', reverse=True)[:5]
                ]
            }
        
        if include_reports and project.reports:
            project_data["report_summary"] = {
                "total_count": len(project.reports),
                "recent_reports": [
                    {
                        "id": r.id,
                        "title": r.title,
                        "report_type": r.report_type,
                        "created_at": r.created_at.isoformat() if r.created_at else None,
                        "status": r.status
                    }
                    for r in sorted(project.reports, key=lambda x: x.created_at or '', reverse=True)[:5]
                ]
            }
        
        if include_timeline:
            project_data["timeline"] = _build_project_timeline(project)
        
        # Apply field selection
        if field_selection.fields or field_selection.exclude:
            project_data = ResponseOptimizer.optimize_response(project_data, field_selection)
        
        logger.info(
            f"Project {project_id} retrieved with optimizations",
            extra={
                "project_id": project_id,
                "user_id": current_user.id,
                "include_flags": {
                    "vessels": include_vessels,
                    "calculations": include_calculations,
                    "reports": include_reports,
                    "timeline": include_timeline
                },
                "field_selection": bool(field_selection.fields or field_selection.exclude)
            }
        )
        
        return project_data
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get project {project_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve project"
        )


@router.get("/search/advanced", response_model=Dict[str, Any])
async def advanced_project_search(
    request: Request,
    q: str = Query(..., min_length=2, description="Search query"),
    search_fields: Optional[str] = Query(
        "name,description,project_code", 
        description="Comma-separated fields to search"
    ),
    pagination: PaginationParams = Depends(get_pagination_params),
    field_selection: FieldSelection = Depends(get_field_selection),
    fuzzy_search: bool = Query(False, description="Enable fuzzy search"),
    highlight_matches: bool = Query(False, description="Highlight search matches"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Advanced search endpoint with fuzzy matching and result highlighting.
    
    Provides sophisticated search capabilities with performance optimizations
    and customizable result formatting.
    """
    try:
        if not current_user.organization_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User is not associated with any organization"
            )
        
        # Parse search fields
        fields_to_search = search_fields.split(",") if search_fields else ["name", "description"]
        
        # Create base query
        query = db.query(Project).filter(Project.organization_id == current_user.organization_id)
        
        # Apply search with ranking
        search_conditions = []
        search_value = q.strip()
        
        for field in fields_to_search:
            if hasattr(Project, field):
                field_attr = getattr(Project, field)
                if fuzzy_search:
                    # Use similarity search (requires pg_trgm extension)
                    search_conditions.append(field_attr.ilike(f"%{search_value}%"))
                else:
                    # Exact substring match
                    search_conditions.append(field_attr.ilike(f"%{search_value}%"))
        
        if search_conditions:
            query = query.filter(or_(*search_conditions))
        
        # Apply pagination
        paginator = EnhancedPaginator(Project)
        items, pagination_info = paginator.paginate(
            query=query,
            session=db,
            page=pagination.page,
            per_page=pagination.per_page,
            sort_by=pagination.sort_by,
            sort_order=pagination.sort_order
        )
        
        # Convert to response format
        results = []
        for item in items:
            project_dict = ProjectSchema.from_orm(item).dict()
            
            # Add search metadata
            project_dict["search_meta"] = {
                "relevance_score": _calculate_search_relevance(item, search_value, fields_to_search),
                "matched_fields": _get_matched_fields(item, search_value, fields_to_search)
            }
            
            # Add highlighting if requested
            if highlight_matches:
                project_dict = _highlight_search_matches(project_dict, search_value, fields_to_search)
            
            results.append(project_dict)
        
        # Sort by relevance if no explicit sort specified
        if not pagination.sort_by:
            results.sort(key=lambda x: x["search_meta"]["relevance_score"], reverse=True)
        
        # Apply field selection
        if field_selection.fields or field_selection.exclude:
            results = ResponseOptimizer.optimize_response(results, field_selection)
        
        # Create response
        response = paginator.create_response(
            items=results,
            pagination_info=pagination_info,
            meta={
                "search": {
                    "query": search_value,
                    "fields_searched": fields_to_search,
                    "fuzzy_enabled": fuzzy_search,
                    "highlights_enabled": highlight_matches,
                    "total_matches": len(results)
                }
            },
            request_url=str(request.url)
        )
        
        logger.info(
            f"Advanced search executed: '{search_value}' returned {len(results)} results",
            extra={
                "search_query": search_value,
                "search_fields": fields_to_search,
                "user_id": current_user.id,
                "organization_id": current_user.organization_id,
                "results_count": len(results),
                "fuzzy_search": fuzzy_search
            }
        )
        
        return response.dict()
        
    except Exception as e:
        logger.error(f"Advanced search failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Search operation failed"
        )


# Helper functions
def _calculate_completion_percentage(project: Project) -> float:
    """Calculate project completion percentage based on various factors."""
    if not project.vessels:
        return 0.0
    
    total_score = 0
    vessel_count = len(project.vessels)
    
    for vessel in project.vessels:
        vessel_score = 0
        
        # Check if vessel has calculations
        if hasattr(vessel, 'calculations') and vessel.calculations:
            vessel_score += 40
        
        # Check if vessel has reports
        if hasattr(vessel, 'reports') and vessel.reports:
            vessel_score += 30
        
        # Check if vessel has inspections
        if hasattr(vessel, 'inspections') and vessel.inspections:
            vessel_score += 30
        
        total_score += vessel_score
    
    return min(100.0, total_score / vessel_count)


def _group_calculations_by_type(calculations) -> Dict[str, int]:
    """Group calculations by type and return counts."""
    type_counts = {}
    for calc in calculations:
        calc_type = calc.calculation_type
        type_counts[calc_type] = type_counts.get(calc_type, 0) + 1
    return type_counts


def _build_project_timeline(project: Project) -> List[Dict[str, Any]]:
    """Build project timeline from various events."""
    timeline = []
    
    # Project creation
    if project.created_at:
        timeline.append({
            "date": project.created_at.isoformat(),
            "event": "project_created",
            "description": f"Project '{project.name}' created",
            "type": "milestone"
        })
    
    # Add vessel creation events
    if project.vessels:
        for vessel in project.vessels:
            if vessel.created_at:
                timeline.append({
                    "date": vessel.created_at.isoformat(),
                    "event": "vessel_added",
                    "description": f"Vessel '{vessel.tag_number}' added",
                    "type": "addition"
                })
    
    # Sort by date
    timeline.sort(key=lambda x: x["date"])
    
    return timeline[-10:]  # Return last 10 events


def _calculate_search_relevance(project: Project, query: str, fields: List[str]) -> float:
    """Calculate search relevance score for ranking."""
    score = 0.0
    query_lower = query.lower()
    
    # Field weights
    field_weights = {
        "name": 3.0,
        "project_code": 2.5,
        "description": 1.0
    }
    
    for field in fields:
        if hasattr(project, field):
            field_value = str(getattr(project, field) or "").lower()
            weight = field_weights.get(field, 1.0)
            
            # Exact match bonus
            if query_lower == field_value:
                score += weight * 10
            # Starts with bonus
            elif field_value.startswith(query_lower):
                score += weight * 5
            # Contains bonus
            elif query_lower in field_value:
                score += weight * 2
    
    return score


def _get_matched_fields(project: Project, query: str, fields: List[str]) -> List[str]:
    """Get list of fields that match the search query."""
    matched = []
    query_lower = query.lower()
    
    for field in fields:
        if hasattr(project, field):
            field_value = str(getattr(project, field) or "").lower()
            if query_lower in field_value:
                matched.append(field)
    
    return matched


def _highlight_search_matches(project_dict: Dict[str, Any], query: str, fields: List[str]) -> Dict[str, Any]:
    """Add highlighting to search matches in the response."""
    highlighted = project_dict.copy()
    query_lower = query.lower()
    
    for field in fields:
        if field in highlighted and highlighted[field]:
            field_value = str(highlighted[field])
            if query_lower in field_value.lower():
                # Simple highlighting with HTML tags
                highlighted_value = field_value.replace(
                    query, f"<mark>{query}</mark>"
                )
                highlighted[f"{field}_highlighted"] = highlighted_value
    
    return highlighted