from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel
from .models import TicketType, TicketStatus

class TicketBase(BaseModel):
    ticket_type: str
    status: str = TicketStatus.pending.value
    created_by: int
    answered_by: Optional[int] = None

class TicketAddDataBase(BaseModel):
    parent_id: int
    name: str

class TicketEditDataBase(BaseModel):
    tree_id: int
    new_name: str
    new_bio: Optional[str] = None
    new_birth: Optional[str] = None
    new_death: Optional[str] = None

class TicketAddDataCreate(TicketAddDataBase):
    pass

class TicketEditDataCreate(TicketEditDataBase):
    pass

class TicketCreate(TicketBase):
    add_data: Optional[List[TicketAddDataCreate]] = None
    edit_data: Optional[TicketEditDataCreate] = None

    class Config:
        json_schema_extra = {
            "example": {
                "ticket_type": "add_data",
                "created_by": 1,
                "add_data": [
                    {
                        "parent_id": 1,
                        "name": "Иван Иванов"
                    },
                    {
                        "parent_id": 1,
                        "name": "Мария Иванова"
                    }
                ]
            }
        }

class TicketAddDataResponse(TicketAddDataBase):
    id: int
    ticket_id: int

    class Config:
        from_attributes = True

class TicketEditDataResponse(TicketEditDataBase):
    id: int
    ticket_id: int

    class Config:
        from_attributes = True

class TicketResponse(TicketBase):
    id: int
    add_data: Optional[List[TicketAddDataResponse]] = None
    edit_data: Optional[TicketEditDataResponse] = None

    class Config:
        from_attributes = True

class TicketListResponse(BaseModel):
    tickets: List[TicketResponse]
