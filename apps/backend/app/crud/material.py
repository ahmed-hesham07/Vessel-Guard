"""
CRUD operations for Material model.

Handles engineering material database with temperature-dependent
properties and ASME compliance data.
"""

from typing import List, Optional
from datetime import datetime

from sqlalchemy import and_, func, or_
from sqlalchemy.orm import Session

from app.crud.base import CRUDBase
from app.db.models.material import Material
from app.schemas.material import MaterialCreate, MaterialUpdate


class CRUDMaterial(CRUDBase[Material, MaterialCreate, MaterialUpdate]):
    """
    CRUD operations for Material model.
    
    Extends base CRUD with material-specific methods
    for engineering property queries and temperature analysis.
    """

    def get_by_organization(
        self, db: Session, *, organization_id: int, skip: int = 0, limit: int = 100
    ) -> List[Material]:
        """
        Get materials by organization.
        
        Args:
            db: Database session
            organization_id: Organization ID
            skip: Number of records to skip
            limit: Maximum records to return
            
        Returns:
            List of materials in organization
        """
        return (
            db.query(Material)
            .filter(Material.organization_id == organization_id)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_public_materials(
        self, db: Session, *, skip: int = 0, limit: int = 100
    ) -> List[Material]:
        """
        Get public (standard) materials.
        
        Args:
            db: Database session
            skip: Number of records to skip
            limit: Maximum records to return
            
        Returns:
            List of public materials
        """
        return (
            db.query(Material)
            .filter(Material.is_public == True)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_by_specification(
        self, db: Session, *, specification: str, skip: int = 0, limit: int = 100
    ) -> List[Material]:
        """
        Get materials by specification.
        
        Args:
            db: Database session
            specification: Material specification (e.g., SA-516 Gr 70)
            skip: Number of records to skip
            limit: Maximum records to return
            
        Returns:
            List of materials with matching specification
        """
        return (
            db.query(Material)
            .filter(Material.specification.ilike(f"%{specification}%"))
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_by_grade(
        self, db: Session, *, grade: str, skip: int = 0, limit: int = 100
    ) -> List[Material]:
        """
        Get materials by grade.
        
        Args:
            db: Database session
            grade: Material grade
            skip: Number of records to skip
            limit: Maximum records to return
            
        Returns:
            List of materials with matching grade
        """
        return (
            db.query(Material)
            .filter(Material.grade.ilike(f"%{grade}%"))
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_by_spec_and_grade(
        self, db: Session, *, specification: str, grade: str, organization_id: Optional[int] = None
    ) -> Optional[Material]:
        """
        Get material by specification and grade.
        
        Args:
            db: Database session
            specification: Material specification
            grade: Material grade
            organization_id: Optional organization filter
            
        Returns:
            Material if found, None otherwise
        """
        query = db.query(Material).filter(
            and_(
                Material.specification == specification,
                Material.grade == grade
            )
        )
        
        if organization_id:
            query = query.filter(
                or_(
                    Material.organization_id == organization_id,
                    Material.is_public == True
                )
            )
        else:
            query = query.filter(Material.is_public == True)
        
        return query.first()

    def get_by_temperature_range(
        self,
        db: Session,
        *,
        min_temp: Optional[float] = None,
        max_temp: Optional[float] = None,
        organization_id: Optional[int] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[Material]:
        """
        Get materials suitable for temperature range.
        
        Args:
            db: Database session
            min_temp: Minimum temperature
            max_temp: Maximum temperature
            organization_id: Optional organization filter
            skip: Number of records to skip
            limit: Maximum records to return
            
        Returns:
            List of materials suitable for temperature range
        """
        query = db.query(Material)
        
        if min_temp is not None:
            query = query.filter(
                or_(
                    Material.min_temp.is_(None),
                    Material.min_temp <= min_temp
                )
            )
        
        if max_temp is not None:
            query = query.filter(
                or_(
                    Material.max_temp.is_(None),
                    Material.max_temp >= max_temp
                )
            )
        
        if organization_id:
            query = query.filter(
                or_(
                    Material.organization_id == organization_id,
                    Material.is_public == True
                )
            )
        else:
            query = query.filter(Material.is_public == True)
        
        return query.offset(skip).limit(limit).all()

    def get_by_minimum_strength(
        self,
        db: Session,
        *,
        min_yield_strength: Optional[float] = None,
        min_tensile_strength: Optional[float] = None,
        organization_id: Optional[int] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[Material]:
        """
        Get materials with minimum strength requirements.
        
        Args:
            db: Database session
            min_yield_strength: Minimum yield strength
            min_tensile_strength: Minimum tensile strength
            organization_id: Optional organization filter
            skip: Number of records to skip
            limit: Maximum records to return
            
        Returns:
            List of materials meeting strength requirements
        """
        query = db.query(Material)
        
        if min_yield_strength is not None:
            query = query.filter(
                Material.yield_strength >= min_yield_strength
            )
        
        if min_tensile_strength is not None:
            query = query.filter(
                Material.tensile_strength >= min_tensile_strength
            )
        
        if organization_id:
            query = query.filter(
                or_(
                    Material.organization_id == organization_id,
                    Material.is_public == True
                )
            )
        else:
            query = query.filter(Material.is_public == True)
        
        return query.offset(skip).limit(limit).all()

    def search(
        self,
        db: Session,
        *,
        query: str,
        organization_id: Optional[int] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[Material]:
        """
        Search materials by name, specification, or grade.
        
        Args:
            db: Database session
            query: Search query
            organization_id: Optional organization filter
            skip: Number of records to skip
            limit: Maximum records to return
            
        Returns:
            List of matching materials
        """
        search_term = f"%{query}%"
        db_query = db.query(Material).filter(
            or_(
                Material.name.ilike(search_term),
                Material.specification.ilike(search_term),
                Material.grade.ilike(search_term),
                Material.description.ilike(search_term)
            )
        )
        
        if organization_id:
            db_query = db_query.filter(
                or_(
                    Material.organization_id == organization_id,
                    Material.is_public == True
                )
            )
        else:
            db_query = db_query.filter(Material.is_public == True)
        
        return db_query.offset(skip).limit(limit).all()

    def get_asme_approved_materials(
        self, db: Session, *, organization_id: Optional[int] = None, skip: int = 0, limit: int = 100
    ) -> List[Material]:
        """
        Get ASME approved materials.
        
        Args:
            db: Database session
            organization_id: Optional organization filter
            skip: Number of records to skip
            limit: Maximum records to return
            
        Returns:
            List of ASME approved materials
        """
        query = db.query(Material).filter(Material.is_asme_approved == True)
        
        if organization_id:
            query = query.filter(
                or_(
                    Material.organization_id == organization_id,
                    Material.is_public == True
                )
            )
        else:
            query = query.filter(Material.is_public == True)
        
        return query.offset(skip).limit(limit).all()

    def get_weldable_materials(
        self, db: Session, *, organization_id: Optional[int] = None, skip: int = 0, limit: int = 100
    ) -> List[Material]:
        """
        Get weldable materials.
        
        Args:
            db: Database session
            organization_id: Optional organization filter
            skip: Number of records to skip
            limit: Maximum records to return
            
        Returns:
            List of weldable materials
        """
        query = db.query(Material).filter(Material.is_weldable == True)
        
        if organization_id:
            query = query.filter(
                or_(
                    Material.organization_id == organization_id,
                    Material.is_public == True
                )
            )
        else:
            query = query.filter(Material.is_public == True)
        
        return query.offset(skip).limit(limit).all()

    def get_carbon_steel_materials(
        self, db: Session, *, organization_id: Optional[int] = None, skip: int = 0, limit: int = 100
    ) -> List[Material]:
        """
        Get carbon steel materials.
        
        Args:
            db: Database session
            organization_id: Optional organization filter
            skip: Number of records to skip
            limit: Maximum records to return
            
        Returns:
            List of carbon steel materials
        """
        query = db.query(Material).filter(
            Material.specification.ilike('%SA-516%') |
            Material.specification.ilike('%A516%') |
            Material.specification.ilike('%SA-285%') |
            Material.specification.ilike('%A285%')
        )
        
        if organization_id:
            query = query.filter(
                or_(
                    Material.organization_id == organization_id,
                    Material.is_public == True
                )
            )
        else:
            query = query.filter(Material.is_public == True)
        
        return query.offset(skip).limit(limit).all()

    def get_stainless_steel_materials(
        self, db: Session, *, organization_id: Optional[int] = None, skip: int = 0, limit: int = 100
    ) -> List[Material]:
        """
        Get stainless steel materials.
        
        Args:
            db: Database session
            organization_id: Optional organization filter
            skip: Number of records to skip
            limit: Maximum records to return
            
        Returns:
            List of stainless steel materials
        """
        query = db.query(Material).filter(
            Material.specification.ilike('%SA-240%') |
            Material.specification.ilike('%A240%') |
            Material.specification.ilike('%304%') |
            Material.specification.ilike('%316%') |
            Material.specification.ilike('%321%') |
            Material.specification.ilike('%347%')
        )
        
        if organization_id:
            query = query.filter(
                or_(
                    Material.organization_id == organization_id,
                    Material.is_public == True
                )
            )
        else:
            query = query.filter(Material.is_public == True)
        
        return query.offset(skip).limit(limit).all()

    def get_material_count_by_organization(
        self, db: Session, *, organization_id: int
    ) -> int:
        """
        Get material count for organization.
        
        Args:
            db: Database session
            organization_id: Organization ID
            
        Returns:
            Material count
        """
        return (
            db.query(func.count(Material.id))
            .filter(Material.organization_id == organization_id)
            .scalar()
        )

    def get_material_statistics(
        self, db: Session, *, organization_id: Optional[int] = None
    ) -> dict:
        """
        Get material statistics.
        
        Args:
            db: Database session
            organization_id: Optional organization filter
            
        Returns:
            Dictionary with material statistics
        """
        query = db.query(Material)
        
        if organization_id:
            query = query.filter(
                or_(
                    Material.organization_id == organization_id,
                    Material.is_public == True
                )
            )
        else:
            query = query.filter(Material.is_public == True)
        
        total_materials = query.count()
        asme_approved = query.filter(Material.is_asme_approved == True).count()
        weldable = query.filter(Material.is_weldable == True).count()
        
        return {
            "total_materials": total_materials,
            "asme_approved": asme_approved,
            "weldable": weldable,
            "asme_approval_percentage": (asme_approved / total_materials * 100) if total_materials > 0 else 0,
            "weldable_percentage": (weldable / total_materials * 100) if total_materials > 0 else 0
        }

    def create_standard_materials(self, db: Session) -> List[Material]:
        """
        Create standard ASME materials if they don't exist.
        
        Args:
            db: Database session
            
        Returns:
            List of created materials
        """
        standard_materials = [
            {
                "name": "SA-516 Grade 70",
                "specification": "SA-516",
                "grade": "70",
                "description": "Carbon Steel Plates for Pressure Vessels",
                "yield_strength": 38000,
                "tensile_strength": 70000,
                "min_temp": -20,
                "max_temp": 650,
                "is_asme_approved": True,
                "is_weldable": True,
                "is_public": True
            },
            {
                "name": "SA-240 Type 304",
                "specification": "SA-240",
                "grade": "304",
                "description": "Stainless Steel Plate for Pressure Vessels",
                "yield_strength": 30000,
                "tensile_strength": 75000,
                "min_temp": -425,
                "max_temp": 1500,
                "is_asme_approved": True,
                "is_weldable": True,
                "is_public": True
            },
            {
                "name": "SA-240 Type 316L",
                "specification": "SA-240",
                "grade": "316L",
                "description": "Low Carbon Stainless Steel Plate",
                "yield_strength": 25000,
                "tensile_strength": 70000,
                "min_temp": -425,
                "max_temp": 1500,
                "is_asme_approved": True,
                "is_weldable": True,
                "is_public": True
            }
        ]
        
        created_materials = []
        
        for mat_data in standard_materials:
            existing = self.get_by_spec_and_grade(
                db, 
                specification=mat_data["specification"],
                grade=mat_data["grade"]
            )
            
            if not existing:
                material = Material(**mat_data)
                db.add(material)
                created_materials.append(material)
        
        if created_materials:
            db.commit()
            for material in created_materials:
                db.refresh(material)
        
        return created_materials


# Create instance for dependency injection
material = CRUDMaterial(Material)
