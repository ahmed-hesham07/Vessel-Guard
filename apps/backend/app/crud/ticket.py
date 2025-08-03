from sqlalchemy.orm import Session
from typing import List, Optional
from app.db.models.ticket import Ticket
from app.schemas.ticket import TicketCreate, TicketUpdate

class TicketCRUD:
    model = Ticket
    
    def get(self, db: Session, id: int) -> Optional[Ticket]:
        return db.query(Ticket).filter(Ticket.id == id).first()

    def get_multi(self, db: Session, skip: int = 0, limit: int = 100) -> List[Ticket]:
        return db.query(Ticket).offset(skip).limit(limit).all()

    def get_multi_filtered(self, db: Session, filters: list, skip: int = 0, limit: int = 100):
        query = db.query(Ticket)
        for f in filters:
            query = query.filter(f)
        return query.offset(skip).limit(limit).all()

    def count_filtered(self, db: Session, filters: list) -> int:
        query = db.query(Ticket)
        for f in filters:
            query = query.filter(f)
        return query.count()

    def create(self, db: Session, obj_in: TicketCreate, user_id: int, organization_id: int) -> Ticket:
        db_obj = Ticket(**obj_in.dict(), user_id=user_id, organization_id=organization_id)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(self, db: Session, db_obj: Ticket, obj_in: TicketUpdate) -> Ticket:
        for field, value in obj_in.dict(exclude_unset=True).items():
            setattr(db_obj, field, value)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def delete(self, db: Session, id: int) -> None:
        obj = db.query(Ticket).filter(Ticket.id == id).first()
        if obj:
            db.delete(obj)
            db.commit()


ticket_crud = TicketCRUD()