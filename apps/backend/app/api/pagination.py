"""
Enhanced pagination utilities for optimized API responses.

Provides efficient pagination, sorting, filtering, and field selection
capabilities for improved API performance and user experience.
"""

from typing import Any, Dict, List, Optional, Type, Union, Tuple, Set
from math import ceil
from fastapi import Query, Request
from sqlalchemy.orm import Session, Query as SQLQuery
from sqlalchemy import desc, asc, func, select
from pydantic import BaseModel, Field

from app.core.logging_config import get_logger

logger = get_logger(__name__)


class PaginationParams(BaseModel):
    """Standardized pagination parameters."""
    page: int = Field(1, ge=1, description="Page number (1-based)")
    per_page: int = Field(50, ge=1, le=1000, description="Items per page")
    sort_by: Optional[str] = Field(None, description="Field to sort by")
    sort_order: str = Field("asc", regex="^(asc|desc)$", description="Sort order")


class FilterParams(BaseModel):
    """Base filtering parameters."""
    search: Optional[str] = Field(None, min_length=1, max_length=100, description="Search query")
    active_only: bool = Field(True, description="Filter to active items only")
    created_after: Optional[str] = Field(None, description="Filter items created after date (ISO format)")
    created_before: Optional[str] = Field(None, description="Filter items created before date (ISO format)")


class FieldSelection(BaseModel):
    """Field selection for response optimization."""
    fields: Optional[str] = Field(None, description="Comma-separated list of fields to include")
    exclude: Optional[str] = Field(None, description="Comma-separated list of fields to exclude")


class PaginatedResponse(BaseModel):
    """Standardized paginated response structure."""
    items: List[Any]
    pagination: Dict[str, Any]
    meta: Optional[Dict[str, Any]] = None

    class Config:
        arbitrary_types_allowed = True


class EnhancedPaginator:
    """Enhanced pagination utility with performance optimizations."""
    
    def __init__(self, model: Type):
        self.model = model
        self.logger = get_logger(f'paginator.{model.__name__.lower()}')
    
    def paginate(
        self,
        query: SQLQuery,
        session: Session,
        page: int = 1,
        per_page: int = 50,
        sort_by: Optional[str] = None,
        sort_order: str = "asc",
        count_query: Optional[SQLQuery] = None,
        use_window_functions: bool = True
    ) -> Tuple[List[Any], Dict[str, Any]]:
        """
        Efficient pagination with optimized counting.
        
        Args:
            query: Base SQLAlchemy query
            session: Database session
            page: Page number (1-based)
            per_page: Items per page
            sort_by: Field to sort by
            sort_order: Sort order (asc/desc)
            count_query: Optional separate count query for optimization
            use_window_functions: Use window functions for better performance
        
        Returns:
            Tuple of (items, pagination_info)
        """
        try:
            # Validate parameters
            page = max(1, page)
            per_page = min(max(1, per_page), 1000)
            offset = (page - 1) * per_page
            
            # Apply sorting if specified
            if sort_by and hasattr(self.model, sort_by):
                sort_column = getattr(self.model, sort_by)
                if sort_order.lower() == "desc":
                    query = query.order_by(desc(sort_column))
                else:
                    query = query.order_by(asc(sort_column))
            else:
                # Default sorting by id or created_at
                if hasattr(self.model, 'created_at'):
                    query = query.order_by(desc(self.model.created_at))
                elif hasattr(self.model, 'id'):
                    query = query.order_by(desc(self.model.id))
            
            # Get total count efficiently
            if count_query is not None:
                total_count = session.scalar(select(func.count()).select_from(count_query.subquery()))
            else:
                # Use the same base query for counting
                count_stmt = select(func.count()).select_from(query.statement.alias())
                total_count = session.scalar(count_stmt)
            
            # Apply pagination
            items = query.offset(offset).limit(per_page).all()
            
            # Calculate pagination metadata
            total_pages = ceil(total_count / per_page) if total_count > 0 else 0
            has_next = page < total_pages
            has_prev = page > 1
            
            pagination_info = {
                "page": page,
                "per_page": per_page,
                "total": total_count,
                "pages": total_pages,
                "has_next": has_next,
                "has_prev": has_prev,
                "next_page": page + 1 if has_next else None,
                "prev_page": page - 1 if has_prev else None,
                "offset": offset,
                "limit": per_page
            }
            
            self.logger.debug(f"Paginated query: {len(items)} items, page {page}/{total_pages}")
            
            return items, pagination_info
            
        except Exception as e:
            self.logger.error(f"Pagination error: {e}")
            # Return empty result on error
            return [], {
                "page": 1,
                "per_page": per_page,
                "total": 0,
                "pages": 0,
                "has_next": False,
                "has_prev": False,
                "next_page": None,
                "prev_page": None,
                "offset": 0,
                "limit": per_page
            }
    
    def create_response(
        self,
        items: List[Any],
        pagination_info: Dict[str, Any],
        meta: Optional[Dict[str, Any]] = None,
        request_url: Optional[str] = None
    ) -> PaginatedResponse:
        """Create a standardized paginated response."""
        
        # Add navigation links if request URL is provided
        if request_url and pagination_info.get("pages", 0) > 1:
            base_url = request_url.split("?")[0]
            links = {}
            
            if pagination_info.get("has_prev"):
                links["prev"] = f"{base_url}?page={pagination_info['prev_page']}"
            
            if pagination_info.get("has_next"):
                links["next"] = f"{base_url}?page={pagination_info['next_page']}"
            
            links["first"] = f"{base_url}?page=1"
            links["last"] = f"{base_url}?page={pagination_info['pages']}"
            
            pagination_info["links"] = links
        
        # Add performance metadata
        if meta is None:
            meta = {}
        
        meta.update({
            "performance": {
                "items_returned": len(items),
                "query_efficient": pagination_info["total"] <= 10000,  # Flag for large datasets
                "pagination_type": "offset"  # Could be extended to cursor-based
            }
        })
        
        return PaginatedResponse(
            items=items,
            pagination=pagination_info,
            meta=meta
        )


class AdvancedFilter:
    """Advanced filtering capabilities for API endpoints."""
    
    def __init__(self, model: Type):
        self.model = model
        self.logger = get_logger(f'filter.{model.__name__.lower()}')
    
    def apply_search(
        self,
        query: SQLQuery,
        search_term: str,
        search_fields: List[str]
    ) -> SQLQuery:
        """Apply full-text search across specified fields."""
        if not search_term or not search_fields:
            return query
        
        search_conditions = []
        search_value = f"%{search_term.lower()}%"
        
        for field_name in search_fields:
            if hasattr(self.model, field_name):
                field = getattr(self.model, field_name)
                search_conditions.append(func.lower(field).contains(search_value))
        
        if search_conditions:
            from sqlalchemy import or_
            query = query.filter(or_(*search_conditions))
        
        return query
    
    def apply_date_filters(
        self,
        query: SQLQuery,
        created_after: Optional[str] = None,
        created_before: Optional[str] = None,
        updated_after: Optional[str] = None,
        updated_before: Optional[str] = None
    ) -> SQLQuery:
        """Apply date range filters."""
        from datetime import datetime
        
        try:
            if created_after and hasattr(self.model, 'created_at'):
                date_after = datetime.fromisoformat(created_after)
                query = query.filter(self.model.created_at >= date_after)
            
            if created_before and hasattr(self.model, 'created_at'):
                date_before = datetime.fromisoformat(created_before)
                query = query.filter(self.model.created_at <= date_before)
            
            if updated_after and hasattr(self.model, 'updated_at'):
                date_after = datetime.fromisoformat(updated_after)
                query = query.filter(self.model.updated_at >= date_after)
            
            if updated_before and hasattr(self.model, 'updated_at'):
                date_before = datetime.fromisoformat(updated_before)
                query = query.filter(self.model.updated_at <= date_before)
                
        except ValueError as e:
            self.logger.warning(f"Invalid date format in filter: {e}")
        
        return query
    
    def apply_active_filter(self, query: SQLQuery, active_only: bool = True) -> SQLQuery:
        """Apply active/inactive filter."""
        if active_only and hasattr(self.model, 'is_active'):
            query = query.filter(self.model.is_active == True)
        
        return query


def get_pagination_params(
    page: int = Query(1, ge=1, description="Page number (1-based)"),
    per_page: int = Query(50, ge=1, le=1000, description="Items per page"),
    sort_by: Optional[str] = Query(None, description="Field to sort by"),
    sort_order: str = Query("asc", regex="^(asc|desc)$", description="Sort order")
) -> PaginationParams:
    """FastAPI dependency for pagination parameters."""
    return PaginationParams(
        page=page,
        per_page=per_page,
        sort_by=sort_by,
        sort_order=sort_order
    )


def get_filter_params(
    search: Optional[str] = Query(None, min_length=1, max_length=100, description="Search query"),
    active_only: bool = Query(True, description="Filter to active items only"),
    created_after: Optional[str] = Query(None, description="Filter items created after date (ISO format)"),
    created_before: Optional[str] = Query(None, description="Filter items created before date (ISO format)")
) -> FilterParams:
    """FastAPI dependency for filter parameters."""
    return FilterParams(
        search=search,
        active_only=active_only,
        created_after=created_after,
        created_before=created_before
    )


def get_field_selection(
    fields: Optional[str] = Query(None, description="Comma-separated list of fields to include"),
    exclude: Optional[str] = Query(None, description="Comma-separated list of fields to exclude")
) -> FieldSelection:
    """FastAPI dependency for field selection."""
    return FieldSelection(fields=fields, exclude=exclude)


class ResponseOptimizer:
    """Optimize API responses with field selection and data transformation."""
    
    @staticmethod
    def optimize_response(
        data: Any,
        field_selection: FieldSelection,
        exclude_null: bool = True
    ) -> Any:
        """Optimize response data based on field selection."""
        if not isinstance(data, (dict, list)):
            return data
        
        # Parse field selection
        include_fields = None
        exclude_fields = set()
        
        if field_selection.fields:
            include_fields = set(field_selection.fields.split(","))
        
        if field_selection.exclude:
            exclude_fields = set(field_selection.exclude.split(","))
        
        # Apply optimization
        if isinstance(data, list):
            return [
                ResponseOptimizer._optimize_item(item, include_fields, exclude_fields, exclude_null)
                for item in data
            ]
        else:
            return ResponseOptimizer._optimize_item(data, include_fields, exclude_fields, exclude_null)
    
    @staticmethod
    def _optimize_item(
        item: Any,
        include_fields: Optional[Set[str]],
        exclude_fields: Set[str],
        exclude_null: bool
    ) -> Any:
        """Optimize a single item."""
        if not isinstance(item, dict):
            # If it's a Pydantic model, convert to dict first
            if hasattr(item, 'dict'):
                item = item.dict()
            elif hasattr(item, '__dict__'):
                item = item.__dict__
            else:
                return item
        
        optimized = {}
        
        for key, value in item.items():
            # Skip excluded fields
            if key in exclude_fields:
                continue
            
            # Include only specified fields if include_fields is set
            if include_fields and key not in include_fields:
                continue
            
            # Skip null values if requested
            if exclude_null and value is None:
                continue
            
            optimized[key] = value
        
        return optimized


# Utility functions
def create_pagination_response(
    items: List[Any],
    total: int,
    page: int,
    per_page: int,
    request: Optional[Request] = None
) -> Dict[str, Any]:
    """Create a standardized pagination response."""
    total_pages = ceil(total / per_page) if total > 0 else 0
    has_next = page < total_pages
    has_prev = page > 1
    
    response = {
        "items": items,
        "pagination": {
            "page": page,
            "per_page": per_page,
            "total": total,
            "pages": total_pages,
            "has_next": has_next,
            "has_prev": has_prev,
            "next_page": page + 1 if has_next else None,
            "prev_page": page - 1 if has_prev else None
        }
    }
    
    # Add navigation links if request is provided
    if request and total_pages > 1:
        base_url = str(request.url).split("?")[0]
        links = {}
        
        if has_prev:
            links["prev"] = f"{base_url}?page={page - 1}"
        
        if has_next:
            links["next"] = f"{base_url}?page={page + 1}"
        
        links["first"] = f"{base_url}?page=1"
        links["last"] = f"{base_url}?page={total_pages}"
        
        response["pagination"]["links"] = links
    
    return response