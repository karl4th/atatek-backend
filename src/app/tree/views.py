from fastapi import APIRouter
from fastapi.params import Depends
from sqlalchemy.ext.asyncio import AsyncSession


from src.app.db.core import get_db
from src.app.config.auth import auth
from src.app.config.response import StandardResponse, autowrap
from .service import TreeService


router = APIRouter(prefix="/api/tree", tags=["tree"])

@router.get('/', response_model=StandardResponse[dict])
@autowrap
async def get_tree(node_id: int, user_data = Depends(auth.get_user_data_dependency()), db: AsyncSession = Depends(get_db)):
    service = TreeService(db)
    return await service.get_tree_on_db(int(node_id), int(user_data["sub"]))

@router.get('/{node_id}', response_model=StandardResponse[dict])
@autowrap
async def get_node_data(node_id: int, db: AsyncSession = Depends(get_db)):
    service = TreeService(db)
    return await service.get_tree_data(int(node_id))

@router.post('/delete/{node_id}', response_model=StandardResponse[dict])
@autowrap
async def delete_tree(node_id: int, db: AsyncSession = Depends(get_db)):
    service = TreeService(db)
    return await service.delete_tree_on_page(int(node_id))

@router.post('/restore/{node_id}', response_model=StandardResponse[dict])
@autowrap
async def restore_tree(node_id: int, db: AsyncSession = Depends(get_db)):
    service = TreeService(db)
    return await service.restore_tree_on_page(int(node_id))

