"""
CRUD operations for Vessel model.

Handles pressure vessel management including design parameters,
inspection tracking, and engineering calculations.
"""

from typing import List, Optional
from datetime import datetime

from sqlalchemy import and_, func, or_
from sqlalchemy.orm import Session

from app.crud.base import CRUDBase
from app.db.models.vessel import Vessel
from app.schemas.vessel import VesselCreate, VesselUpdate


class CRUDVessel(CRUDBase[Vessel, VesselCreate, VesselUpdate]):
    """
    CRUD operations for Vessel model.
    
    Extends base CRUD with vessel-specific methods
    for engineering analysis and inspection management.
    """

    def get_by_project(
        self, db: Session, *, project_id: int, skip: int = 0, limit: int = 100
    ) -> List[Vessel]:
        """
        Get vessels by project.
        
        Args:
            db: Database session
            project_id: Project ID
            skip: Number of records to skip
            limit: Maximum records to return
            
        Returns:
            List of vessels in project
        """
        return (
            db.query(Vessel)
            .filter(Vessel.project_id == project_id)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_by_organization(
        self, db: Session, *, organization_id: int, skip: int = 0, limit: int = 100
    ) -> List[Vessel]:
        """
        Get vessels by organization.
        
        Args:
            db: Database session
            organization_id: Organization ID
            skip: Number of records to skip
            limit: Maximum records to return
            
        Returns:
            List of vessels in organization
        """
        return (
            db.query(Vessel)
            .filter(Vessel.organization_id == organization_id)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_by_tag_number(
        self, db: Session, *, tag_number: str, organization_id: int
    ) -> Optional[Vessel]:
        """
        Get vessel by tag number within organization.
        
        Args:
            db: Database session
            tag_number: Vessel tag number
            organization_id: Organization ID
            
        Returns:
            Vessel if found, None otherwise
        """
        return (
            db.query(Vessel)
            .filter(
                and_(
                    Vessel.tag_number == tag_number,
                    Vessel.organization_id == organization_id
                )
            )
            .first()
        )

    def get_by_vessel_type(
        self,
        db: Session,
        *,
        vessel_type: str,
        organization_id: Optional[int] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[Vessel]:
        """
        Get vessels by type.
        
        Args:
            db: Database session
            vessel_type: Vessel type
            organization_id: Optional organization filter
            skip: Number of records to skip
            limit: Maximum records to return
            
        Returns:
            List of vessels with matching type
        """
        query = db.query(Vessel).filter(Vessel.vessel_type == vessel_type)
        
        if organization_id:
            query = query.filter(Vessel.organization_id == organization_id)
        
        return query.offset(skip).limit(limit).all()

    def get_by_design_code(
        self,
        db: Session,
        *,
        design_code: str,
        organization_id: Optional[int] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[Vessel]:
        """
        Get vessels by design code.
        
        Args:
            db: Database session
            design_code: Design code (e.g., ASME VIII)
            organization_id: Optional organization filter
            skip: Number of records to skip
            limit: Maximum records to return
            
        Returns:
            List of vessels with matching design code
        """
        query = db.query(Vessel).filter(Vessel.design_code == design_code)
        
        if organization_id:
            query = query.filter(Vessel.organization_id == organization_id)
        
        return query.offset(skip).limit(limit).all()

    def get_due_for_inspection(
        self,
        db: Session,
        *,
        days_ahead: int = 30,
        organization_id: Optional[int] = None
    ) -> List[Vessel]:
        """
        Get vessels due for inspection.
        
        Args:
            db: Database session
            days_ahead: Number of days to look ahead
            organization_id: Optional organization filter
            
        Returns:
            List of vessels due for inspection
        """
        from datetime import timedelta
        
        future_date = datetime.utcnow() + timedelta(days=days_ahead)
        
        query = db.query(Vessel).filter(
            and_(
                Vessel.next_inspection_date.isnot(None),
                Vessel.next_inspection_date <= future_date,
                Vessel.is_active == True
            )
        )
        
        if organization_id:
            query = query.filter(Vessel.organization_id == organization_id)
        
        return query.all()

    def get_overdue_for_inspection(
        self, db: Session, *, organization_id: Optional[int] = None
    ) -> List[Vessel]:
        """
        Get vessels overdue for inspection.
        
        Args:
            db: Database session
            organization_id: Optional organization filter
            
        Returns:
            List of vessels overdue for inspection
        """
        query = db.query(Vessel).filter(
            and_(
                Vessel.next_inspection_date.isnot(None),
                Vessel.next_inspection_date < datetime.utcnow(),
                Vessel.is_active == True
            )
        )
        
        if organization_id:
            query = query.filter(Vessel.organization_id == organization_id)
        
        return query.all()

    def search(
        self,
        db: Session,
        *,
        query: str,
        organization_id: Optional[int] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[Vessel]:
        """
        Search vessels by tag number, name, or description.
        
        Args:
            db: Database session
            query: Search query
            organization_id: Optional organization filter
            skip: Number of records to skip
            limit: Maximum records to return
            
        Returns:
            List of matching vessels
        """
        search_term = f"%{query}%"
        db_query = db.query(Vessel).filter(
            or_(
                Vessel.tag_number.ilike(search_term),
                Vessel.name.ilike(search_term),
                Vessel.description.ilike(search_term),
                Vessel.service.ilike(search_term)
            )
        )
        
        if organization_id:
            db_query = db_query.filter(Vessel.organization_id == organization_id)
        
        return db_query.offset(skip).limit(limit).all()

    def get_by_pressure_range(
        self,
        db: Session,
        *,
        min_pressure: Optional[float] = None,
        max_pressure: Optional[float] = None,
        organization_id: Optional[int] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[Vessel]:
        """
        Get vessels by operating pressure range.
        
        Args:
            db: Database session
            min_pressure: Minimum operating pressure
            max_pressure: Maximum operating pressure
            organization_id: Optional organization filter
            skip: Number of records to skip
            limit: Maximum records to return
            
        Returns:
            List of vessels within pressure range
        """
        query = db.query(Vessel)
        
        if min_pressure is not None:
            query = query.filter(Vessel.operating_pressure >= min_pressure)
        
        if max_pressure is not None:
            query = query.filter(Vessel.operating_pressure <= max_pressure)
        
        if organization_id:
            query = query.filter(Vessel.organization_id == organization_id)
        
        return query.offset(skip).limit(limit).all()

    def get_by_temperature_range(
        self,
        db: Session,
        *,
        min_temperature: Optional[float] = None,
        max_temperature: Optional[float] = None,
        organization_id: Optional[int] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[Vessel]:
        """
        Get vessels by operating temperature range.
        
        Args:
            db: Database session
            min_temperature: Minimum operating temperature
            max_temperature: Maximum operating temperature
            organization_id: Optional organization filter
            skip: Number of records to skip
            limit: Maximum records to return
            
        Returns:
            List of vessels within temperature range
        """
        query = db.query(Vessel)
        
        if min_temperature is not None:
            query = query.filter(Vessel.operating_temperature >= min_temperature)
        
        if max_temperature is not None:
            query = query.filter(Vessel.operating_temperature <= max_temperature)
        
        if organization_id:
            query = query.filter(Vessel.organization_id == organization_id)
        
        return query.offset(skip).limit(limit).all()

    def update_inspection_date(
        self, db: Session, *, vessel_id: int, next_inspection_date: datetime
    ) -> Vessel:
        """
        Update next inspection date.
        
        Args:
            db: Database session
            vessel_id: Vessel ID
            next_inspection_date: Next inspection date
            
        Returns:
            Updated vessel
        """
        vessel = self.get_or_404(db, id=vessel_id)
        
        vessel.next_inspection_date = next_inspection_date
        vessel.updated_at = datetime.utcnow()
        
        db.add(vessel)
        db.commit()
        db.refresh(vessel)
        return vessel

    def get_vessel_count_by_project(
        self, db: Session, *, project_id: int
    ) -> int:
        """
        Get vessel count for project.
        
        Args:
            db: Database session
            project_id: Project ID
            
        Returns:
            Vessel count
        """
        return (
            db.query(func.count(Vessel.id))
            .filter(Vessel.project_id == project_id)
            .scalar()
        )

    def get_vessel_count_by_organization(
        self, db: Session, *, organization_id: int
    ) -> int:
        """
        Get vessel count for organization.
        
        Args:
            db: Database session
            organization_id: Organization ID
            
        Returns:
            Vessel count
        """
        return (
            db.query(func.count(Vessel.id))
            .filter(Vessel.organization_id == organization_id)
            .scalar()
        )

    def get_vessels_by_material(
        self,
        db: Session,
        *,
        material_id: int,
        organization_id: Optional[int] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[Vessel]:
        """
        Get vessels using specific material.
        
        Args:
            db: Database session
            material_id: Material ID
            organization_id: Optional organization filter
            skip: Number of records to skip
            limit: Maximum records to return
            
        Returns:
            List of vessels using the material
        """
        query = db.query(Vessel).filter(Vessel.material_id == material_id)
        
        if organization_id:
            query = query.filter(Vessel.organization_id == organization_id)
        
        return query.offset(skip).limit(limit).all()

    def get_critical_vessels(
        self, db: Session, *, organization_id: Optional[int] = None
    ) -> List[Vessel]:
        """
        Get vessels that require immediate attention.
        
        Args:
            db: Database session
            organization_id: Optional organization filter
            
        Returns:
            List of critical vessels
        """
        # Vessels are critical if:
        # 1. Overdue for inspection
        # 2. High pressure and temperature combination
        # 3. Marked as critical service
        
        query = db.query(Vessel).filter(
            or_(
                # Overdue for inspection
                and_(
                    Vessel.next_inspection_date.isnot(None),
                    Vessel.next_inspection_date < datetime.utcnow()
                ),
                # High pressure (>1000 psi) and high temperature (>400F)
                and_(
                    Vessel.operating_pressure > 1000,
                    Vessel.operating_temperature > 400
                ),
                # Service contains 'critical' or 'toxic' or 'flammable'
                or_(
                    Vessel.service.ilike('%critical%'),
                    Vessel.service.ilike('%toxic%'),
                    Vessel.service.ilike('%flammable%')
                )
            )
        ).filter(Vessel.is_active == True)
        
        if organization_id:
            query = query.filter(Vessel.organization_id == organization_id)
        
        return query.all()

    def get_vessel_statistics(
        self, db: Session, *, organization_id: int
    ) -> dict:
        """
        Get vessel statistics for organization.
        
        Args:
            db: Database session
            organization_id: Organization ID
            
        Returns:
            Dictionary with vessel statistics
        """
        total_vessels = self.get_vessel_count_by_organization(
            db, organization_id=organization_id
        )
        
        # Count by type
        type_counts = {}
        for vessel_type in ["pressure_vessel", "storage_tank", "heat_exchanger", "reactor", "column"]:
            count = (
                db.query(func.count(Vessel.id))
                .filter(
                    and_(
                        Vessel.organization_id == organization_id,
                        Vessel.vessel_type == vessel_type
                    )
                )
                .scalar()
            )
            type_counts[vessel_type] = count
        
        # Count by design code
        code_counts = {}
        for code in ["ASME VIII Div 1", "ASME VIII Div 2", "API 650", "API 620", "PD 5500"]:
            count = (
                db.query(func.count(Vessel.id))
                .filter(
                    and_(
                        Vessel.organization_id == organization_id,
                        Vessel.design_code == code
                    )
                )
                .scalar()
            )
            code_counts[code] = count
        
        overdue_count = len(self.get_overdue_for_inspection(db, organization_id=organization_id))
        due_soon_count = len(self.get_due_for_inspection(db, organization_id=organization_id))
        critical_count = len(self.get_critical_vessels(db, organization_id=organization_id))
        
        return {
            "total_vessels": total_vessels,
            "type_breakdown": type_counts,
            "code_breakdown": code_counts,
            "overdue_inspections": overdue_count,
            "due_soon_inspections": due_soon_count,
            "critical_vessels": critical_count
        }


# Create instance for dependency injection
vessel = CRUDVessel(Vessel)
