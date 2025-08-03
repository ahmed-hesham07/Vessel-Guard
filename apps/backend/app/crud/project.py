"""
CRUD operations for Project model.

Handles project management including timeline tracking,
collaboration, and organization-based access control.

UPDATED: Added field mapping for schema-model compatibility
"""

from typing import List, Optional, Union, Dict, Any
from datetime import datetime

from sqlalchemy import and_, func, or_
from sqlalchemy.orm import Session

from app.crud.base import CRUDBase
from app.db.models.project import Project
from app.db.models.user import User
from app.schemas.project import ProjectCreate, ProjectUpdate


class CRUDProject(CRUDBase[Project, ProjectCreate, ProjectUpdate]):
    """
    CRUD operations for Project model.
    
    Extends base CRUD with project-specific methods
    for timeline management and collaboration features.
    """

    def create(self, db: Session, *, obj_in: Union[ProjectCreate, Dict[str, Any]]) -> Project:
        """
        Create new project with field mapping.
        
        Maps schema fields to model fields, handling the end_date -> target_completion_date
        mapping and other field transformations.
        """
        from fastapi.encoders import jsonable_encoder
        
        # Convert input to dict and handle field mapping
        if isinstance(obj_in, dict):
            obj_in_data = obj_in.copy()
        else:
            obj_in_data = jsonable_encoder(obj_in)
        
        print(f"DEBUG: Original obj_in_data keys: {list(obj_in_data.keys())}")  # Debug log
        print(f"DEBUG: Original obj_in_data: {obj_in_data}")  # Debug log
        
        # Map end_date to target_completion_date if present
        if 'end_date' in obj_in_data and obj_in_data['end_date'] is not None:
            obj_in_data['target_completion_date'] = obj_in_data.pop('end_date')
            print(f"DEBUG: Mapped end_date to target_completion_date")  # Debug log
        else:
            print(f"DEBUG: No end_date found or it was None")  # Debug log
        
        # Map created_by_id to owner_id if present
        if 'created_by_id' in obj_in_data:
            obj_in_data['owner_id'] = obj_in_data.pop('created_by_id')
            print(f"DEBUG: Mapped created_by_id to owner_id")  # Debug log
        else:
            print(f"DEBUG: No created_by_id found")  # Debug log
        
        # Remove budget field as it's not in the Project model
        if 'budget' in obj_in_data:
            budget_value = obj_in_data.pop('budget')
            print(f"DEBUG: Removed budget field (value: {budget_value})")  # Debug log
        
        # Map status values from schema to model enum
        status_mapping = {
            "planning": "active",
            "in_progress": "active", 
            "review": "active",
            "completed": "completed",
            "cancelled": "cancelled",
            "on_hold": "on_hold"
        }
        if 'status' in obj_in_data and obj_in_data['status'] in status_mapping:
            original_status = obj_in_data['status']
            mapped_status = status_mapping[obj_in_data['status']]
            obj_in_data['status'] = mapped_status
            print(f"DEBUG: Mapped status from {original_status} to {mapped_status}")  # Debug log
        
        print(f"DEBUG: Final obj_in_data keys: {list(obj_in_data.keys())}")  # Debug log
        print(f"DEBUG: Final obj_in_data: {obj_in_data}")  # Debug log
        
        # Create the project with mapped fields
        try:
            db_obj = Project(**obj_in_data)
            print(f"DEBUG: Project created successfully")  # Debug log
        except Exception as e:
            print(f"DEBUG: Error creating Project: {e}")  # Debug log
            print(f"DEBUG: Problematic keys: {list(obj_in_data.keys())}")  # Debug log
            raise
        
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(self, db: Session, *, db_obj: Project, obj_in: Union[ProjectUpdate, Dict[str, Any]]) -> Project:
        """
        Update project with field mapping.
        
        Maps schema fields to model fields, handling the end_date -> target_completion_date
        mapping and other field transformations.
        """
        from fastapi.encoders import jsonable_encoder
        
        # Convert schema to dict and handle field mapping
        obj_data = jsonable_encoder(db_obj)
        
        if isinstance(obj_in, dict):
            update_data = obj_in.copy()
        else:
            update_data = obj_in.dict(exclude_unset=True)
        
        # Map end_date to target_completion_date if present
        if 'end_date' in update_data and update_data['end_date'] is not None:
            update_data['target_completion_date'] = update_data.pop('end_date')
        
        # Map created_by_id to owner_id if present
        if 'created_by_id' in update_data:
            update_data['owner_id'] = update_data.pop('created_by_id')
        
        # Map status values from schema to model enum
        status_mapping = {
            "planning": "active",
            "in_progress": "active", 
            "review": "active",
            "completed": "completed",
            "cancelled": "cancelled",
            "on_hold": "on_hold"
        }
        if 'status' in update_data and update_data['status'] in status_mapping:
            update_data['status'] = status_mapping[update_data['status']]
        
        # Update fields
        for field in obj_data:
            if field in update_data:
                setattr(db_obj, field, update_data[field])
        
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def get_by_organization(
        self, db: Session, *, organization_id: int, skip: int = 0, limit: int = 100
    ) -> List[Project]:
        """
        Get projects by organization.
        
        Args:
            db: Database session
            organization_id: Organization ID
            skip: Number of records to skip
            limit: Maximum records to return
            
        Returns:
            List of projects in organization
        """
        return (
            db.query(Project)
            .filter(Project.organization_id == organization_id)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_active_by_organization(
        self, db: Session, *, organization_id: int, skip: int = 0, limit: int = 100
    ) -> List[Project]:
        """
        Get active projects by organization.
        
        Args:
            db: Database session
            organization_id: Organization ID
            skip: Number of records to skip
            limit: Maximum records to return
            
        Returns:
            List of active projects in organization
        """
        return (
            db.query(Project)
            .filter(
                and_(
                    Project.organization_id == organization_id,
                    Project.status == "active"
                )
            )
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_by_owner(
        self, db: Session, *, owner_id: int, skip: int = 0, limit: int = 100
    ) -> List[Project]:
        """
        Get projects by owner.
        
        Args:
            db: Database session
            owner_id: Owner user ID
            skip: Number of records to skip
            limit: Maximum records to return
            
        Returns:
            List of projects owned by user
        """
        return (
            db.query(Project)
            .filter(Project.owner_id == owner_id)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_by_status(
        self,
        db: Session,
        *,
        status: str,
        organization_id: Optional[int] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[Project]:
        """
        Get projects by status.
        
        Args:
            db: Database session
            status: Project status
            organization_id: Optional organization filter
            skip: Number of records to skip
            limit: Maximum records to return
            
        Returns:
            List of projects with matching status
        """
        query = db.query(Project).filter(Project.status == status)
        
        if organization_id:
            query = query.filter(Project.organization_id == organization_id)
        
        return query.offset(skip).limit(limit).all()

    def get_overdue_projects(
        self, db: Session, *, organization_id: Optional[int] = None
    ) -> List[Project]:
        """
        Get projects that are overdue.
        
        Args:
            db: Database session
            organization_id: Optional organization filter
            
        Returns:
            List of overdue projects
        """
        query = db.query(Project).filter(
            and_(
                Project.target_completion_date.isnot(None),
                Project.target_completion_date < datetime.utcnow(),
                Project.status.notin_(["completed", "cancelled"])
            )
        )
        
        if organization_id:
            query = query.filter(Project.organization_id == organization_id)
        
        return query.all()

    def get_due_soon(
        self,
        db: Session,
        *,
        days_ahead: int = 7,
        organization_id: Optional[int] = None
    ) -> List[Project]:
        """
        Get projects due soon.
        
        Args:
            db: Database session
            days_ahead: Number of days to look ahead
            organization_id: Optional organization filter
            
        Returns:
            List of projects due within specified days
        """
        from datetime import timedelta
        
        future_date = datetime.utcnow() + timedelta(days=days_ahead)
        
        query = db.query(Project).filter(
            and_(
                Project.target_completion_date.isnot(None),
                Project.target_completion_date <= future_date,
                Project.target_completion_date >= datetime.utcnow(),
                Project.status.notin_(["completed", "cancelled"])
            )
        )
        
        if organization_id:
            query = query.filter(Project.organization_id == organization_id)
        
        return query.all()

    def search(
        self,
        db: Session,
        *,
        query: str,
        organization_id: Optional[int] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[Project]:
        """
        Search projects by name or description.
        
        Args:
            db: Database session
            query: Search query
            organization_id: Optional organization filter
            skip: Number of records to skip
            limit: Maximum records to return
            
        Returns:
            List of matching projects
        """
        search_term = f"%{query}%"
        db_query = db.query(Project).filter(
            or_(
                Project.name.ilike(search_term),
                Project.description.ilike(search_term),
                Project.project_number.ilike(search_term)
            )
        )
        
        if organization_id:
            db_query = db_query.filter(Project.organization_id == organization_id)
        
        return db_query.offset(skip).limit(limit).all()

    def get_by_project_number(
        self, db: Session, *, project_number: str, organization_id: int
    ) -> Optional[Project]:
        """
        Get project by project number within organization.
        
        Args:
            db: Database session
            project_number: Project number
            organization_id: Organization ID
            
        Returns:
            Project if found, None otherwise
        """
        return (
            db.query(Project)
            .filter(
                and_(
                    Project.project_number == project_number,
                    Project.organization_id == organization_id
                )
            )
            .first()
        )

    def update_status(
        self, db: Session, *, project_id: int, status: str, updated_by_id: int
    ) -> Project:
        """
        Update project status.
        
        Args:
            db: Database session
            project_id: Project ID
            status: New status
            updated_by_id: User ID making the update
            
        Returns:
            Updated project
        """
        project = self.get(db, id=project_id)
        if not project:
            raise ValueError(f"Project with ID {project_id} not found")
        
        project.status = status
        # Note: The model doesn't have updated_by_id field, so we skip that
        
        # Set completion date if completed
        if status == "completed" and not project.actual_completion_date:
            project.actual_completion_date = datetime.utcnow()
        
        db.add(project)
        db.commit()
        db.refresh(project)
        return project

    def complete_project(
        self, db: Session, *, project_id: int, completed_by_id: int
    ) -> Project:
        """
        Mark project as completed.
        
        Args:
            db: Database session
            project_id: Project ID
            completed_by_id: User ID completing the project
            
        Returns:
            Completed project
        """
        return self.update_status(
            db, project_id=project_id, status="completed", updated_by_id=completed_by_id
        )

    def get_project_count_by_organization(
        self, db: Session, *, organization_id: int
    ) -> int:
        """
        Get total project count for organization.
        
        Args:
            db: Database session
            organization_id: Organization ID
            
        Returns:
            Total project count
        """
        return (
            db.query(func.count(Project.id))
            .filter(Project.organization_id == organization_id)
            .scalar()
        )

    def get_active_project_count_by_organization(
        self, db: Session, *, organization_id: int
    ) -> int:
        """
        Get active project count for organization.
        
        Args:
            db: Database session
            organization_id: Organization ID
            
        Returns:
            Active project count
        """
        return (
            db.query(func.count(Project.id))
            .filter(
                and_(
                    Project.organization_id == organization_id,
                    Project.status == "active"
                )
            )
            .scalar()
        )

    def can_create_project(self, db: Session, *, organization_id: int) -> bool:
        """
        Check if organization can create a new project.
        
        Args:
            db: Database session
            organization_id: Organization ID
            
        Returns:
            True if organization can create projects, False otherwise
        """
        from app.crud.organization import organization as org_crud
        
        org = org_crud.get(db, id=organization_id)
        if not org or not org.is_active:
            return False
        
        # Check project limit
        if org.max_projects:
            current_count = self.get_active_project_count_by_organization(
                db, organization_id=organization_id
            )
            if current_count >= org.max_projects:
                return False
        
        return True

    def get_recent_projects(
        self,
        db: Session,
        *,
        organization_id: int,
        days: int = 30,
        limit: int = 10
    ) -> List[Project]:
        """
        Get recently created projects.
        
        Args:
            db: Database session
            organization_id: Organization ID
            days: Number of days to look back
            limit: Maximum projects to return
            
        Returns:
            List of recent projects
        """
        from datetime import timedelta
        
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        return (
            db.query(Project)
            .filter(
                and_(
                    Project.organization_id == organization_id,
                    Project.created_at >= cutoff_date
                )
            )
            .order_by(Project.created_at.desc())
            .limit(limit)
            .all()
        )

    def get_project_statistics(
        self, db: Session, *, organization_id: int
    ) -> dict:
        """
        Get project statistics for organization.
        
        Args:
            db: Database session
            organization_id: Organization ID
            
        Returns:
            Dictionary with project statistics
        """
        total_projects = self.get_project_count_by_organization(
            db, organization_id=organization_id
        )
        active_projects = self.get_active_project_count_by_organization(
            db, organization_id=organization_id
        )
        
        # Count by status
        status_counts = {}
        for status in ["planning", "in_progress", "review", "completed", "cancelled"]:
            count = (
                db.query(func.count(Project.id))
                .filter(
                    and_(
                        Project.organization_id == organization_id,
                        Project.status == status
                    )
                )
                .scalar()
            )
            status_counts[status] = count
        
        overdue_count = len(self.get_overdue_projects(db, organization_id=organization_id))
        due_soon_count = len(self.get_due_soon(db, organization_id=organization_id))
        
        return {
            "total_projects": total_projects,
            "active_projects": active_projects,
            "status_breakdown": status_counts,
            "overdue_projects": overdue_count,
            "due_soon_projects": due_soon_count
        }


# Create instance for dependency injection
project = CRUDProject(Project)
