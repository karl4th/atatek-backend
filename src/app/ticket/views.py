from fastapi import APIRouter, Response
from fastapi.params import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from src.app.config.response import *
from src.app.db.core import get_db
from src.app.ticket.service import TicketService
from src.app.ticket.schemas import *
from src.app.config.auth import auth

router = APIRouter()

@router.post("/create", response_model=StandardResponse[TicketResponse])
@autowrap
async def create_ticket(ticket: TicketCreate, user_data = Depends(auth.get_user_data_dependency()), db: AsyncSession = Depends(get_db)):
    user_id = int(user_data["sub"])
    service = TicketService(db)
    new_ticket = await service.create_ticket(ticket, user_id)
    return new_ticket

@router.get("/my", response_model=StandardResponse[List[TicketResponse]])
@autowrap
async def get_tickets_by_user(user_data = Depends(auth.get_user_data_dependency()), db: AsyncSession = Depends(get_db)):
    user_id = int(user_data["sub"])
    service = TicketService(db)
    tickets = await service.get_tickets_by_user(user_id)
    return tickets


@router.get("/details/{ticket_id}", response_model=StandardResponse[TicketResponse])
@autowrap
async def get_ticket_details(ticket_id: int, user_data = Depends(auth.get_user_data_dependency()), db: AsyncSession = Depends(get_db)):
    user_id = int(user_data["sub"])
    service = TicketService(db)
    ticket = await service.get_ticket_details(ticket_id)
    return ticket

@router.get("/admin/all", response_model=StandardResponse[TicketListResponse])
@autowrap
async def get_all_tickets(user_data = Depends(auth.get_user_data_dependency()), db: AsyncSession = Depends(get_db)):
    user_id = int(user_data["sub"])
    service = TicketService(db)
    tickets = await service.get_tickets(user_id)
    return tickets

@router.put("/admin/status/{ticket_id}/{status}", response_model=StandardResponse[TicketResponse])
@autowrap
async def change_ticket_status(ticket_id: int, status: str, user_data = Depends(auth.get_user_data_dependency()), db: AsyncSession = Depends(get_db)):
    user_id = int(user_data["sub"])
    service = TicketService(db)
    ticket = await service.change_ticket_status(user_id, ticket_id, status)
    return ticket
