"""
Base CRUD operations for database models.

Provides generic CRUD operations that can be inherited
by specific model CRUD classes.
"""

from typing import Any, Dict, Generic, List, Optional, Type, TypeVar, Union

from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy.ext.declarative import DeclarativeMeta

ModelType = TypeVar("ModelType", bound=DeclarativeMeta)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class CRUDBase(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    """
    Base CRUD operations.
    
    Generic class providing common database operations
    for SQLAlchemy models with Pydantic schema validation.
    """

    def __init__(self, model: Type[ModelType]):
        """
        Initialize CRUD object with model class.
        
        Args:
            model: SQLAlchemy model class
        """
        self.model = model

    def get(self, db: Session, id: Any) -> Optional[ModelType]:
        """
        Get record by ID.
        
        Args:
            db: Database session
            id: Record ID
            
        Returns:
            Model instance if found, None otherwise
        """
        return db.query(self.model).filter(self.model.id == id).first()

    def get_multi(
        self, db: Session, *, skip: int = 0, limit: int = 100
    ) -> List[ModelType]:
        """
        Get multiple records with pagination.
        
        Args:
            db: Database session
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of model instances
        """
        return db.query(self.model).offset(skip).limit(limit).all()

    def create(self, db: Session, *, obj_in: CreateSchemaType) -> ModelType:
        """
        Create new record.
        
        Args:
            db: Database session
            obj_in: Pydantic schema with creation data
            
        Returns:
            Created model instance
        """
        obj_in_data = jsonable_encoder(obj_in)
        db_obj = self.model(**obj_in_data)  # type: ignore
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(
        self,
        db: Session,
        *,
        db_obj: ModelType,
        obj_in: Union[UpdateSchemaType, Dict[str, Any]]
    ) -> ModelType:
        """
        Update existing record.
        
        Args:
            db: Database session
            db_obj: Existing model instance
            obj_in: Update data (Pydantic schema or dict)
            
        Returns:
            Updated model instance
        """
        obj_data = jsonable_encoder(db_obj)
        
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.dict(exclude_unset=True)
        
        for field in obj_data:
            if field in update_data:
                setattr(db_obj, field, update_data[field])
        
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def delete(self, db: Session, *, id: int) -> ModelType:
        """
        Delete record by ID.
        
        Args:
            db: Database session
            id: Record ID
            
        Returns:
            Deleted model instance
            
        Raises:
            ValueError: If record not found
        """
        obj = db.query(self.model).get(id)
        if not obj:
            raise ValueError(f"Record with id {id} not found")
        
        db.delete(obj)
        db.commit()
        return obj

    def count(self, db: Session) -> int:
        """
        Count total number of records.
        
        Args:
            db: Database session
            
        Returns:
            Total record count
        """
        return db.query(self.model).count()

    def exists(self, db: Session, *, id: int) -> bool:
        """
        Check if record exists.
        
        Args:
            db: Database session
            id: Record ID
            
        Returns:
            True if record exists, False otherwise
        """
        return db.query(self.model).filter(self.model.id == id).first() is not None

    def get_or_404(self, db: Session, *, id: int) -> ModelType:
        """
        Get record by ID or raise exception.
        
        Args:
            db: Database session
            id: Record ID
            
        Returns:
            Model instance
            
        Raises:
            ValueError: If record not found
        """
        obj = self.get(db, id=id)
        if not obj:
            raise ValueError(f"Record with id {id} not found")
        return obj

    def create_with_owner(
        self, db: Session, *, obj_in: CreateSchemaType, owner_id: int
    ) -> ModelType:
        """
        Create record with owner relationship.
        
        Args:
            db: Database session
            obj_in: Creation data
            owner_id: Owner user ID
            
        Returns:
            Created model instance
        """
        obj_in_data = jsonable_encoder(obj_in)
        db_obj = self.model(**obj_in_data, owner_id=owner_id)  # type: ignore
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def get_multi_by_owner(
        self, db: Session, *, owner_id: int, skip: int = 0, limit: int = 100
    ) -> List[ModelType]:
        """
        Get multiple records by owner.
        
        Args:
            db: Database session
            owner_id: Owner user ID
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of model instances
        """
        return (
            db.query(self.model)
            .filter(self.model.owner_id == owner_id)  # type: ignore
            .offset(skip)
            .limit(limit)
            .all()
        )

    def soft_delete(self, db: Session, *, id: int) -> ModelType:
        """
        Soft delete record (mark as inactive).
        
        Args:
            db: Database session
            id: Record ID
            
        Returns:
            Updated model instance
            
        Raises:
            ValueError: If record not found or doesn't support soft delete
        """
        obj = self.get_or_404(db, id=id)
        
        if not hasattr(obj, 'is_active'):
            raise ValueError("Model does not support soft delete")
        
        obj.is_active = False  # type: ignore
        db.add(obj)
        db.commit()
        db.refresh(obj)
        return obj

    def restore(self, db: Session, *, id: int) -> ModelType:
        """
        Restore soft deleted record.
        
        Args:
            db: Database session
            id: Record ID
            
        Returns:
            Updated model instance
            
        Raises:
            ValueError: If record not found or doesn't support soft delete
        """
        obj = self.get_or_404(db, id=id)
        
        if not hasattr(obj, 'is_active'):
            raise ValueError("Model does not support soft delete")
        
        obj.is_active = True  # type: ignore
        db.add(obj)
        db.commit()
        db.refresh(obj)
        return obj
