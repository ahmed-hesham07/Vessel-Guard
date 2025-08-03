"""
Material API endpoints.

Handles engineering materials database including ASME properties,
temperature dependencies, and standard material configurations.
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
from app.crud import material as material_crud
from app.db.models.user import User
from app.schemas import (
    Material,
    MaterialCreate,
    MaterialUpdate,
    MaterialList,
    MaterialSummary,
    MaterialProperty,
    MaterialPropertyRange,
    MaterialStatistics,
    MaterialDashboard
)

router = APIRouter()


@router.get("/", response_model=MaterialList)
def get_materials(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    search: Optional[str] = Query(None, min_length=1),
    material_type: Optional[str] = Query(None),
    specification: Optional[str] = Query(None),
    is_standard: Optional[bool] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get materials in user's organization or standard materials.
    
    Supports filtering by type, specification, and search.
    """
    if not current_user.organization_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User is not associated with any organization"
        )
    
    # Apply filters
    if search:
        materials = material_crud.search(
            db, query=search, organization_id=current_user.organization_id, skip=skip, limit=limit
        )
        total = len(material_crud.search(
            db, query=search, organization_id=current_user.organization_id, skip=0, limit=10000
        ))
    elif specification:
        materials = material_crud.get_by_specification(
            db, specification=specification, organization_id=current_user.organization_id, skip=skip, limit=limit
        )
        total = len(material_crud.get_by_specification(
            db, specification=specification, organization_id=current_user.organization_id, skip=0, limit=10000
        ))
    elif material_type:
        materials = material_crud.get_by_material_type(
            db, material_type=material_type, organization_id=current_user.organization_id, skip=skip, limit=limit
        )
        total = len(material_crud.get_by_material_type(
            db, material_type=material_type, organization_id=current_user.organization_id, skip=0, limit=10000
        ))
    elif is_standard is not None:
        if is_standard:
            materials = material_crud.get_standard_materials(db, skip=skip, limit=limit)
            total = len(material_crud.get_standard_materials(db, skip=0, limit=10000))
        else:
            materials = material_crud.get_custom_materials(
                db, organization_id=current_user.organization_id, skip=skip, limit=limit
            )
            total = len(material_crud.get_custom_materials(
                db, organization_id=current_user.organization_id, skip=0, limit=10000
            ))
    else:
        materials = material_crud.get_by_organization(
            db, organization_id=current_user.organization_id, skip=skip, limit=limit
        )
        total = material_crud.get_material_count_by_organization(
            db, organization_id=current_user.organization_id
        )
    
    return MaterialList(
        items=materials,
        total=total,
        page=skip // limit + 1,
        per_page=limit,
        pages=(total + limit - 1) // limit
    )


@router.post("/", response_model=Material, status_code=status.HTTP_201_CREATED)
def create_material(
    material_in: MaterialCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["engineer", "admin"]))
):
    """
    Create new material.
    
    Engineers and admins can create materials in their organization.
    """
    if not current_user.organization_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User is not associated with any organization"
        )
    
    # Check if material designation already exists in organization
    existing_material = material_crud.get_by_designation(
        db, 
        designation=material_in.designation,
        organization_id=current_user.organization_id
    )
    if existing_material:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Material with this designation already exists in organization"
        )
    
    # Create material data
    material_data = material_in.dict()
    material_data.update({
        "organization_id": current_user.organization_id,
        "created_by_id": current_user.id,
        "is_standard": False  # Custom materials are not standard
    })
    
    material = material_crud.create(db, obj_in=material_data)
    return material


@router.get("/dashboard", response_model=MaterialDashboard)
def get_material_dashboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get material dashboard data for user's organization.
    """
    if not current_user.organization_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User is not associated with any organization"
        )
    
    # Get recent materials
    recent_materials = material_crud.get_by_organization(
        db, organization_id=current_user.organization_id, skip=0, limit=5
    )
    
    # Get most used materials
    most_used_materials = material_crud.get_most_used_materials(
        db, organization_id=current_user.organization_id, limit=5
    )
    
    # Get ASME compliant materials
    asme_materials = material_crud.get_asme_compliant_materials(
        db, organization_id=current_user.organization_id, limit=10
    )
    
    # Get statistics
    statistics = material_crud.get_material_statistics(
        db, organization_id=current_user.organization_id
    )
    
    return MaterialDashboard(
        recent_materials=[MaterialSummary.from_orm(m) for m in recent_materials],
        most_used_materials=[MaterialSummary.from_orm(m) for m in most_used_materials],
        asme_compliant_materials=[MaterialSummary.from_orm(m) for m in asme_materials],
        statistics=MaterialStatistics(**statistics)
    )


@router.get("/statistics", response_model=MaterialStatistics)
def get_material_statistics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get material statistics for user's organization.
    """
    if not current_user.organization_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User is not associated with any organization"
        )
    
    statistics = material_crud.get_material_statistics(
        db, organization_id=current_user.organization_id
    )
    
    return MaterialStatistics(**statistics)


@router.get("/standard", response_model=List[Material])
def get_standard_materials(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get standard ASME materials available to all organizations.
    """
    materials = material_crud.get_standard_materials(db, skip=skip, limit=limit)
    return materials


@router.get("/asme-compliant", response_model=List[Material])
def get_asme_compliant_materials(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get ASME compliant materials for user's organization.
    """
    if not current_user.organization_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User is not associated with any organization"
        )
    
    materials = material_crud.get_asme_compliant_materials(
        db, organization_id=current_user.organization_id, skip=skip, limit=limit
    )
    
    return materials


@router.get("/most-used", response_model=List[Material])
def get_most_used_materials(
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get most frequently used materials in organization.
    """
    if not current_user.organization_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User is not associated with any organization"
        )
    
    materials = material_crud.get_most_used_materials(
        db, organization_id=current_user.organization_id, limit=limit
    )
    
    return materials


@router.get("/search/by-properties", response_model=List[Material])
def search_materials_by_properties(
    min_yield_strength: Optional[float] = Query(None, ge=0),
    max_yield_strength: Optional[float] = Query(None, ge=0),
    min_tensile_strength: Optional[float] = Query(None, ge=0),
    max_tensile_strength: Optional[float] = Query(None, ge=0),
    min_allowable_stress: Optional[float] = Query(None, ge=0),
    max_allowable_stress: Optional[float] = Query(None, ge=0),
    temperature: Optional[float] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Search materials by mechanical properties.
    """
    if not current_user.organization_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User is not associated with any organization"
        )
    
    materials = material_crud.get_by_property_range(
        db,
        min_yield_strength=min_yield_strength,
        max_yield_strength=max_yield_strength,
        min_tensile_strength=min_tensile_strength,
        max_tensile_strength=max_tensile_strength,
        min_allowable_stress=min_allowable_stress,
        max_allowable_stress=max_allowable_stress,
        temperature=temperature,
        organization_id=current_user.organization_id,
        skip=skip,
        limit=limit
    )
    
    return materials


@router.get("/search/by-temperature", response_model=List[Material])
def search_materials_by_temperature(
    min_temperature: Optional[float] = Query(None),
    max_temperature: Optional[float] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Search materials by temperature range.
    """
    if not current_user.organization_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User is not associated with any organization"
        )
    
    materials = material_crud.get_by_temperature_range(
        db,
        min_temperature=min_temperature,
        max_temperature=max_temperature,
        organization_id=current_user.organization_id,
        skip=skip,
        limit=limit
    )
    
    return materials


@router.get("/{material_id}", response_model=Material)
def get_material(
    material_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get material by ID.
    
    Users can access standard materials or materials in their organization.
    """
    material = material_crud.get(db, id=material_id)
    if not material:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Material not found"
        )
    
    # Check permissions
    if (current_user.role != "super_admin" and 
        not material.is_standard and
        material.organization_id != current_user.organization_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to access this material"
        )
    
    return material


@router.get("/{material_id}/properties", response_model=MaterialProperty)
def get_material_properties(
    material_id: int,
    temperature: Optional[float] = Query(None, description="Temperature for property calculation"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get material properties at specified temperature.
    """
    material = material_crud.get(db, id=material_id)
    if not material:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Material not found"
        )
    
    # Check permissions
    if (current_user.role != "super_admin" and 
        not material.is_standard and
        material.organization_id != current_user.organization_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to access this material"
        )
    
    # Calculate properties at temperature
    properties = {
        "material_id": material.id,
        "designation": material.designation,
        "temperature": temperature or 20.0,  # Default to room temperature
        "yield_strength": material.yield_strength,
        "tensile_strength": material.tensile_strength,
        "allowable_stress": material.allowable_stress,
        "modulus_of_elasticity": material.modulus_of_elasticity,
        "thermal_expansion": material.thermal_expansion,
        "thermal_conductivity": material.thermal_conductivity,
        "density": material.density,
        "max_temperature": material.max_temperature,
        "min_temperature": material.min_temperature,
        "is_asme_compliant": material.is_asme_compliant
    }
    
    return MaterialProperty(**properties)


@router.put("/{material_id}", response_model=Material)
def update_material(
    material_id: int,
    material_in: MaterialUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["engineer", "admin"]))
):
    """
    Update material.
    
    Engineers and admins can update materials in their organization.
    Standard materials can only be updated by super admins.
    """
    material = material_crud.get(db, id=material_id)
    if not material:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Material not found"
        )
    
    # Check permissions
    if material.is_standard and current_user.role != "super_admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only super admins can update standard materials"
        )
    
    if (current_user.role != "super_admin" and 
        material.organization_id != current_user.organization_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to update this material"
        )
    
    # Check for designation conflicts
    if (material_in.designation and 
        material_in.designation != material.designation):
        existing_material = material_crud.get_by_designation(
            db,
            designation=material_in.designation,
            organization_id=material.organization_id
        )
        if existing_material:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Material with this designation already exists in organization"
            )
    
    # Add updated_by information
    update_data = material_in.dict(exclude_unset=True)
    update_data["updated_by_id"] = current_user.id
    
    material = material_crud.update(db, db_obj=material, obj_in=update_data)
    return material


@router.delete("/{material_id}", response_model=Material)
def deactivate_material(
    material_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["admin"]))
):
    """
    Deactivate material (soft delete).
    
    Only organization admins and super admins can deactivate materials.
    Standard materials cannot be deactivated.
    """
    material = material_crud.get(db, id=material_id)
    if not material:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Material not found"
        )
    
    # Standard materials cannot be deactivated
    if material.is_standard:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Standard materials cannot be deactivated"
        )
    
    # Check permissions
    if (current_user.role != "super_admin" and 
        material.organization_id != current_user.organization_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to deactivate this material"
        )
    
    material = material_crud.soft_delete(db, id=material_id)
    return material


@router.post("/seed-standard", response_model=dict)
def seed_standard_materials(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["admin"]))
):
    """
    Seed database with standard ASME materials.
    
    Only super admins can seed standard materials.
    """
    count = material_crud.create_standard_materials(db)
    return {"message": f"Created {count} standard materials"}


@router.get("/types/available", response_model=List[str])
def get_available_material_types():
    """
    Get available material types.
    """
    return [
        "carbon_steel", "low_alloy_steel", "stainless_steel", 
        "aluminum", "titanium", "copper", "nickel_alloy", "other"
    ]


@router.get("/specifications/available", response_model=List[str])
def get_available_specifications():
    """
    Get available material specifications.
    """
    return [
        "SA-516 Gr 70", "SA-515 Gr 70", "SA-387 Gr 22", "SA-240 TP 304",
        "SA-240 TP 316", "SA-240 TP 321", "SA-213 TP 304", "SA-213 TP 316",
        "SA-106 Gr B", "SA-335 P11", "SA-335 P22", "SA-335 P91",
        "Other"
    ]
