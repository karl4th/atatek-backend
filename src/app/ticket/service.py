from src.app.ticket.models import *
from src.app.ticket.schemas import *
from src.app.role.service import RoleService
from src.app.tariff.service import TariffService
from src.app.tree.models import Tree
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException

class TicketService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.role_service = RoleService(db)
        self.tariff_service = TariffService(db) 

    async def _set_edit_data(self, ticket_id: int) -> bool:
        try:
            print(f"Starting _set_edit_data for ticket {ticket_id}")
            ticket = await self.db.execute(select(Ticket).where(Ticket.id == ticket_id))
            ticket = ticket.scalars().first()
            if not ticket:
                raise HTTPException(status_code=404, detail="Тикет не найден")
            
            data = await self.db.execute(select(TicketEditData).where(TicketEditData.ticket_id == ticket_id))
            result = data.scalars().first()
            if not result:
                raise HTTPException(status_code=404, detail="Данные для редактирования не найдены")
            
            print(f"Found edit data: {result.__dict__}")
            
            tree = await self.db.execute(select(Tree).where(Tree.id == result.tree_id))
            tree = tree.scalars().first()
            if not tree:
                raise HTTPException(status_code=404, detail="Дерево не найдено")
            
            print(f"Current tree data: {tree.__dict__}")
            
            if result.new_name:
                tree.name = result.new_name
            if result.new_bio:
                tree.bio = result.new_bio
            if result.new_birth:
                tree.birth = result.new_birth
            if result.new_death:
                tree.death = result.new_death

            
            await self.tariff_service._change_edit_count(ticket.created_by)
            await self.db.flush()
            return True
        except Exception as e:
            print(f"Error in _set_edit_data: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Ошибка при обновлении данных: {str(e)}")

    async def _set_add_data(self, ticket_id: int) -> bool:
        try:
            print(f"Starting _set_add_data for ticket {ticket_id}")
            ticket = await self.db.execute(select(Ticket).where(Ticket.id == ticket_id))
            ticket = ticket.scalars().first()
            if not ticket:
                raise HTTPException(status_code=404, detail="Тикет не найден")
            
            data = await self.db.execute(select(TicketAddData).where(TicketAddData.ticket_id == ticket_id))
            result = data.scalars().all()
            if not result:
                raise HTTPException(status_code=404, detail="Данные для добавления не найдены")
            
            print(f"Found {len(result)} items to add")
            
            for item in result:
                print(f"Adding new tree item: {item.__dict__}")
                new_data = Tree(
                    name=item.name,
                    birth=None,
                    death=None,
                    bio=None,
                    is_deleted=False,
                    t_id=0,
                    parent_id=item.parent_id
                )
                self.db.add(new_data)
                await self.db.flush()
            
            await self.tariff_service._change_add_count(ticket.created_by, len(result))
            print("Successfully added all items")
            
            return True
        except Exception as e:
            await self.db.rollback()
            print(f"Error in _set_add_data: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Ошибка при добавлении данных: {str(e)}")
        

    async def create_ticket(self, data: TicketCreate, user_id: int):
        # Создаем основной тикет
        ticket = Ticket(
            ticket_type=data.ticket_type,
            status=data.status,
            created_by=user_id,
            answered_by=data.answered_by
        )
        self.db.add(ticket)
        await self.db.flush()

        # Создаем связанные данные в зависимости от типа тикета
        if data.ticket_type == "add_data" and data.add_data:
            add_data_entries = [
                TicketAddData(
                    ticket_id=ticket.id,
                    parent_id=entry.parent_id,
                    name=entry.name
                )
                for entry in data.add_data
            ]
            self.db.add_all(add_data_entries)
        elif data.ticket_type == "edit_data" and data.edit_data:
            edit_data = TicketEditData(
                ticket_id=ticket.id,
                tree_id=data.edit_data.tree_id,
                new_name=data.edit_data.new_name,
                new_bio=data.edit_data.new_bio,
                new_birth=data.edit_data.new_birth,
                new_death=data.edit_data.new_death
            )
            self.db.add(edit_data)
            await self.db.flush()

        await self.db.commit()
        await self.db.refresh(ticket)

        # Получаем полные данные для ответа
        if data.ticket_type == "add_data":
            query = select(TicketAddData).where(TicketAddData.ticket_id == ticket.id)
            result = await self.db.execute(query)
            add_data = result.scalars().all()
            return TicketResponse(
                id=ticket.id,
                ticket_type=ticket.ticket_type.value,
                status=ticket.status.value,
                created_by=ticket.created_by,
                answered_by=ticket.answered_by,
                add_data=[{
                    'id': item.id,
                    'ticket_id': item.ticket_id,
                    'parent_id': item.parent_id,
                    'name': item.name
                } for item in add_data]
            ).model_dump()
        else:
            query = select(TicketEditData).where(TicketEditData.ticket_id == ticket.id)
            result = await self.db.execute(query)
            edit_data = result.scalars().first()
            
            edit_data_dict = None
            if edit_data:
                edit_data_dict = {
                    'id': edit_data.id,
                    'ticket_id': edit_data.ticket_id,
                    'tree_id': edit_data.tree_id,
                    'new_name': edit_data.new_name,
                    'new_bio': edit_data.new_bio,
                    'new_birth': edit_data.new_birth,
                    'new_death': edit_data.new_death
                }

            return TicketResponse(
                id=ticket.id,
                ticket_type=ticket.ticket_type.value,
                status=ticket.status.value,
                created_by=ticket.created_by,
                answered_by=ticket.answered_by,
                edit_data=edit_data_dict
            ).model_dump()

    async def get_tickets_by_user(self, user_id: int):
        # Получаем все тикеты пользователя
        query = select(Ticket).where(Ticket.created_by == user_id)
        result = await self.db.execute(query)
        tickets = result.scalars().all()
        
        tickets_response = []
        for ticket in tickets:
            # Для каждого тикета получаем связанные данные
            if ticket.ticket_type == "add_data":
                query = select(TicketAddData).where(TicketAddData.ticket_id == ticket.id)
                result = await self.db.execute(query)
                add_data = result.scalars().all()
                tickets_response.append(TicketResponse(
                    id=ticket.id,
                    ticket_type=ticket.ticket_type.value,
                    status=ticket.status.value,
                    created_by=ticket.created_by,
                    answered_by=ticket.answered_by,
                    add_data=[{
                        'id': item.id,
                        'ticket_id': item.ticket_id,
                        'parent_id': item.parent_id,
                        'name': item.name
                    } for item in add_data]
                ).model_dump())
            else:
                query = select(TicketEditData).where(TicketEditData.ticket_id == ticket.id)
                result = await self.db.execute(query)
                edit_data = result.scalars().first()
                
                edit_data_dict = None
                if edit_data:
                    edit_data_dict = {
                        'id': edit_data.id,
                        'ticket_id': edit_data.ticket_id,
                        'tree_id': edit_data.tree_id,
                        'new_name': edit_data.new_name,
                        'new_bio': edit_data.new_bio,
                        'new_birth': edit_data.new_birth,
                        'new_death': edit_data.new_death
                    }
                
                tickets_response.append(TicketResponse(
                    id=ticket.id,
                    ticket_type=ticket.ticket_type.value,
                    status=ticket.status.value,
                    created_by=ticket.created_by,
                    answered_by=ticket.answered_by,
                    edit_data=edit_data_dict
                ).model_dump())
        
        return tickets_response

    async def get_ticket_details(self, ticket_id: int):
        # Получаем основной тикет
        query = select(Ticket).where(Ticket.id == ticket_id)
        result = await self.db.execute(query)
        ticket = result.scalars().first()
        
        if not ticket:
            return None
        
        # Получаем связанные данные в зависимости от типа тикета
        if ticket.ticket_type == "add_data":
            query = select(TicketAddData).where(TicketAddData.ticket_id == ticket.id)
            result = await self.db.execute(query)
            add_data = result.scalars().all()
            return TicketResponse(
                id=ticket.id,
                ticket_type=ticket.ticket_type.value,
                status=ticket.status.value,
                created_by=ticket.created_by,
                answered_by=ticket.answered_by,
                add_data=[{
                    'id': item.id,
                    'ticket_id': item.ticket_id,
                    'parent_id': item.parent_id,
                    'name': item.name
                } for item in add_data]
            ).model_dump()
        else:
            query = select(TicketEditData).where(TicketEditData.ticket_id == ticket.id)
            result = await self.db.execute(query)
            edit_data = result.scalars().first()
            
            edit_data_dict = None
            if edit_data:
                edit_data_dict = {
                    'id': edit_data.id,
                    'ticket_id': edit_data.ticket_id,
                    'tree_id': edit_data.tree_id,
                    'new_name': edit_data.new_name,
                    'new_bio': edit_data.new_bio,
                    'new_birth': edit_data.new_birth,
                    'new_death': edit_data.new_death
                }
            
            return TicketResponse(
                id=ticket.id,
                ticket_type=ticket.ticket_type.value,
                status=ticket.status.value,
                created_by=ticket.created_by,
                answered_by=ticket.answered_by,
                edit_data=edit_data_dict
            ).model_dump()
        
    async def get_tickets(self, user_id: int) -> TicketListResponse:
        user_role = await self.role_service.get_user_role(user_id)
        if user_role != 3:
            raise HTTPException(status_code=403, detail="У вас нет прав на просмотр тикетов")
        
        query = select(Ticket).order_by(Ticket.created_at.desc())
        result = await self.db.execute(query)
        tickets = result.scalars().all()

        return TicketListResponse(
            tickets=[
                TicketResponse(
                    id=ticket.id,
                    ticket_type=ticket.ticket_type.value,
                    status=ticket.status.value,
                    created_by=ticket.created_by,
                    answered_by=ticket.answered_by
                )
                for ticket in tickets
                ]
            ).model_dump()
    
    async def change_ticket_status(self, user_id: int, ticket_id: int, status: str) -> TicketResponse:
        try:
            user_role = await self.role_service.get_user_role(user_id)
            if user_role != 3:
                raise HTTPException(status_code=403, detail="У вас нет прав на изменение статуса тикетов")
            
            ticket = await self.db.execute(select(Ticket).where(Ticket.id == ticket_id))
            ticket = ticket.scalars().first()
            type = ticket.ticket_type
            if not ticket:
                raise HTTPException(status_code=404, detail="Тикет не найден")
            
            print(f"Changing ticket {ticket_id} status from {ticket.status} to {status}")
            ticket.status = status
            await self.db.flush()
            
            if status == "approved":
                print(f"Processing approved ticket {ticket_id} of type {type}")
                if type == "add_data" or ticket.ticket_type.value == "add_data":
                    result = await self._set_add_data(ticket_id)
                    print(f"Add data result: {result}")
                elif type == "edit_data" or ticket.ticket_type.value == "edit_data":
                    result = await self._set_edit_data(ticket_id)
                    print(f"Edit data result: {result}")
            
            await self.db.commit()
            await self.db.refresh(ticket)
            
            return TicketResponse(
                id=ticket.id,
                ticket_type=ticket.ticket_type.value,
                status=ticket.status.value,
                created_by=ticket.created_by,
                answered_by=ticket.answered_by
            ).model_dump()
        except Exception as e:
            await self.db.rollback()
            raise HTTPException(status_code=500, detail=f"Ошибка при изменении статуса тикета: {str(e)}")

        

