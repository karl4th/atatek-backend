from fastapi import APIRouter, Body
from fastapi.params import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Dict, Any

from src.app.db.core import get_db
from src.app.config.auth import auth
from src.app.config.response import StandardResponse, autowrap
from src.app.aulet.schemas import *
from src.app.aulet.service import AuletService

router = APIRouter(prefix="/api/aulet", tags=["menin-auletim"])


@router.get('/my', response_model=StandardResponse[List[Dict[str, Any]]])
@autowrap
async def get_aulet_tree(
    user_data = Depends(auth.get_user_data_dependency()),
    db: AsyncSession = Depends(get_db),
):
    """Получить семейное дерево пользователя в формате family-chart"""
    user_id = int(user_data["sub"])
    service = AuletService(db)
    return await service.get_aulet_tree(user_id)

@router.post('/my/create', response_model=StandardResponse[Dict[str, Any]])
@autowrap
async def create_aulet_person(
    person: CreatePerson = Body(...),
    user_data = Depends(auth.get_user_data_dependency()),
    db: AsyncSession = Depends(get_db),
):
    """Создать новую персону в семейном дереве"""
    user_id = int(user_data["sub"])
    service = AuletService(db)
    return await service.create_aulet_person(user_id, person)

@router.put('/my/update/{person_id}', response_model=StandardResponse[Dict[str, Any]])
@autowrap
async def update_aulet_person(
    person_id: int,
    update_data: UpdatePerson = Body(...),
    user_data = Depends(auth.get_user_data_dependency()),
    db: AsyncSession = Depends(get_db),
):
    """Обновить персону в семейном дереве"""
    user_id = int(user_data["sub"])
    service = AuletService(db)
    
    # Устанавливаем person_id из URL
    update_data.person_id = person_id
    
    return await service.update_aulet_person(user_id, update_data)

@router.delete('/my/delete/{person_id}', response_model=StandardResponse[bool])
@autowrap
async def delete_aulet_person(
    person_id: int,
    user_data = Depends(auth.get_user_data_dependency()),
    db: AsyncSession = Depends(get_db),
):
    """Удалить персону из семейного дерева"""
    user_id = int(user_data["sub"])
    service = AuletService(db)
    return await service.delete_aulet_person(user_id, person_id)