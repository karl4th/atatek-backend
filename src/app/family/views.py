from fastapi import APIRouter
from fastapi.params import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.app.db.core import get_db
from src.app.config.auth import auth
from src.app.config.response import StandardResponse, autowrap
from src.app.family.schemas import *
from src.app.family.service import FamilyService

router = APIRouter(prefix="/api/family", tags=["family"])


@router.post('/create', response_model=StandardResponse[FamilyResponse])
@autowrap
async def create_family_node(
    node: FamilyCreate,
    user_data = Depends(auth.get_user_data_dependency()),
    db: AsyncSession = Depends(get_db),
    father_id: int = None,
    mother_id: int = None,
    partner_id: int = None,
):
    service = FamilyService(db)
    return await service.create_node(
        int(user_data["sub"]),
        node,
        father_id,
        mother_id,
        partner_id,
    )

@router.get('/tree', response_model=StandardResponse[FamilyTree])
@autowrap
async def get_family_tree(
    user_data = Depends(auth.get_user_data_dependency()),
    db: AsyncSession = Depends(get_db),
):
    user_id = int(user_data["sub"])
    service = FamilyService(db)
    return await service.get_family_tree(user_id)

@router.put('/tree/node/{node_id}', response_model=StandardResponse[FamilyResponse])
@autowrap
async def update_family_node(
    node_id: int,
    node: UpdateNode,
    user_data = Depends(auth.get_user_data_dependency()),
    db: AsyncSession = Depends(get_db),
):
    user_id = int(user_data["sub"])
    service = FamilyService(db)
    return await service.update_node(node_id, node)

@router.delete('/tree/node/{node_id}', response_model=StandardResponse[dict])
@autowrap
async def delete_family_node(
    node_id: int,
    user_data = Depends(auth.get_user_data_dependency()),
    db: AsyncSession = Depends(get_db),
):
    service = FamilyService(db)
    return await service.delete_user(int(user_data["sub"]), node_id)
