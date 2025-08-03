from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
import enum

class TicketStatus(str, enum.Enum):
    open = 'open'
    in_progress = 'in_progress'
    resolved = 'resolved'
    closed = 'closed'

class TicketPriority(str, enum.Enum):
    low = 'low'
    medium = 'medium'
    high = 'high'
    urgent = 'urgent'

class TicketCategory(str, enum.Enum):
    technical = 'technical'
    billing = 'billing'
    general = 'general'
    feature_request = 'feature_request'

class TicketBase(BaseModel):
    subject: str
    status: TicketStatus = TicketStatus.open
    priority: TicketPriority = TicketPriority.medium
    category: TicketCategory = TicketCategory.general
    description: str

class TicketCreate(TicketBase):
    pass

class TicketUpdate(BaseModel):
    subject: Optional[str]
    status: Optional[TicketStatus]
    priority: Optional[TicketPriority]
    category: Optional[TicketCategory]
    description: Optional[str]

class TicketInDB(TicketBase):
    id: int
    created_at: datetime
    updated_at: datetime
    user_id: int
    organization_id: int

    class Config:
        from_attributes = True

class TicketResponse(TicketInDB):
    pass

class TicketList(BaseModel):
    items: List[TicketResponse]
    total: int
    page: int
    per_page: int
    pages: int