from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import List, Optional
from app.api.dependencies import get_db, get_current_user
from app.schemas.ticket import TicketCreate, TicketUpdate, TicketResponse, TicketList
from app.crud.ticket import ticket_crud
from app.db.models.user import User

router = APIRouter()

@router.get("/", response_model=TicketList)
def get_tickets(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    status: Optional[str] = Query(None),
    priority: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    filters = [
        (ticket_crud.model.organization_id == current_user.organization_id)
    ]
    if status:
        filters.append(ticket_crud.model.status == status)
    if priority:
        filters.append(ticket_crud.model.priority == priority)
    if category:
        filters.append(ticket_crud.model.category == category)
    if search:
        filters.append(ticket_crud.model.subject.ilike(f"%{search}%"))
    items = ticket_crud.get_multi_filtered(db, filters, skip=skip, limit=limit)
    total = ticket_crud.count_filtered(db, filters)
    return TicketList(
        items=items,
        total=total,
        page=(skip // limit) + 1,
        per_page=limit,
        pages=(total + limit - 1) // limit
    )

@router.post("/", response_model=TicketResponse, status_code=status.HTTP_201_CREATED)
def create_ticket(
    ticket_in: TicketCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    ticket = ticket_crud.create(db, ticket_in, user_id=current_user.id, organization_id=current_user.organization_id)
    return ticket

@router.get("/{ticket_id}", response_model=TicketResponse)
def get_ticket(
    ticket_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    ticket = ticket_crud.get(db, ticket_id)
    if not ticket or ticket.organization_id != current_user.organization_id:
        raise HTTPException(status_code=404, detail="Ticket not found")
    return ticket

@router.put("/{ticket_id}", response_model=TicketResponse)
def update_ticket(
    ticket_id: int,
    ticket_in: TicketUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    ticket = ticket_crud.get(db, ticket_id)
    if not ticket or ticket.organization_id != current_user.organization_id:
        raise HTTPException(status_code=404, detail="Ticket not found")
    ticket = ticket_crud.update(db, ticket, ticket_in)
    return ticket

@router.delete("/{ticket_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_ticket(
    ticket_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    ticket = ticket_crud.get(db, ticket_id)
    if not ticket or ticket.organization_id != current_user.organization_id:
        raise HTTPException(status_code=404, detail="Ticket not found")
    ticket_crud.delete(db, ticket_id)