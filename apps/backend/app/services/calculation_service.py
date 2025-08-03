"""
Calculation service layer for handling calculation-related business logic.
"""

from typing import List, Optional
from sqlalchemy.orm import Session

from app.db.models.calculation import Calculation
from app.schemas.calculation import CalculationCreate
from app.services.calculation_engine import get_calculator
from app.core.exceptions import ValidationError, NotFoundError


class CalculationService:
    """Service class for calculation operations."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_calculation(self, calculation_data: CalculationCreate, vessel_id: int,
                          project_id: int, organization_id: int, performed_by_id: int) -> Calculation:
        """Create a new calculation."""
        db_calculation = Calculation(
            name=calculation_data.name,
            calculation_type=calculation_data.calculation_type,
            description=calculation_data.description,
            input_parameters=calculation_data.input_parameters,
            vessel_id=vessel_id,
            project_id=project_id,
            organization_id=organization_id,
            performed_by_id=performed_by_id,
            status="pending",
            is_active=True
        )
        
        self.db.add(db_calculation)
        self.db.commit()
        self.db.refresh(db_calculation)
        return db_calculation
    
    def perform_calculation(self, calculation_data: CalculationCreate, vessel_id: int,
                           project_id: int, organization_id: int, performed_by_id: int) -> Calculation:
        """Perform calculation and store results."""
        # Create calculation record
        calculation = self.create_calculation(
            calculation_data, vessel_id, project_id, organization_id, performed_by_id
        )
        
        try:
            # Get appropriate calculator
            calculator = get_calculator("asme_viii")
            
            # Perform calculation
            results = calculator.calculate(calculation_data.input_parameters)
            
            # Update calculation with results
            calculation.output_parameters = results
            calculation.status = "completed"
            
            self.db.commit()
            self.db.refresh(calculation)
            return calculation
            
        except Exception as e:
            calculation.status = "failed"
            calculation.error_message = str(e)
            self.db.commit()
            raise
    
    def get_vessel_calculations(self, vessel_id: int) -> List[Calculation]:
        """Get all calculations for a vessel."""
        return self.db.query(Calculation).filter(
            Calculation.vessel_id == vessel_id
        ).all()
