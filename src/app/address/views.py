from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.app.address.service import AddressService
from src.app.config.auth import auth
from src.app.db.core import get_db

router = APIRouter(prefix="/api/address", tags=["address"])


@router.get("/")
async def search_address(query: str, user_data: dict = Depends(auth.get_current_user_dependency()), db: AsyncSession = Depends(get_db)):
    service = AddressService(db)
    location = await service.search_locations(query)
    return {"data": query, "results": location}
