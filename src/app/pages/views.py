from fastapi import APIRouter
from fastapi.params import Depends
from sqlalchemy.ext.asyncio import AsyncSession


from src.app.db.core import get_db
from src.app.config.auth import auth
from src.app.config.response import StandardResponse, autowrap
from src.app.pages.service import PageService
from src.app.pages.schemas import *


router = APIRouter(prefix="/api/pages", tags=["pages"])

@router.post("/create", response_model=StandardResponse[PageResponse])
@autowrap
async def create_page(page: CreatePage, user_data = Depends(auth.get_user_data_dependency()), db: AsyncSession = Depends(get_db)):
    user_id = int(user_data["sub"])
    service = PageService(db)
    return await service.create_page(page, user_id)

@router.get("/{page_id}", response_model=StandardResponse[PageResponse])
@autowrap
async def get_page_by_id(page_id: int, user_data = Depends(auth.get_user_data_dependency()), db: AsyncSession = Depends(get_db)):
    service = PageService(db)
    return await service.get_page_by_id(page_id)

@router.get("/page/{main_gen_juz}", response_model=StandardResponse[PageResponseList])
@autowrap
async def get_juz_data(main_gen_juz: int, user_data = Depends(auth.get_user_data_dependency()), db: AsyncSession = Depends(get_db)):
    service = PageService(db)
    return await service.get_pages_from_main_juz(main_gen_juz, int(user_data["sub"]))


@router.post("/{page_id}/moderator", response_model=StandardResponse[PageResponse])
@autowrap
async def set_moderator(page_id: int, moderator_id: int, user_data = Depends(auth.get_user_data_dependency()), db: AsyncSession = Depends(get_db)):
    user_id = int(user_data["sub"])
    service = PageService(db)
    return await service.set_moderator(page_id, moderator_id, user_id) 

@router.get("/moderator/{moderator_id}", response_model=StandardResponse[PageResponseList])
@autowrap
async def moderator_pages(moderator_id: int, user_data = Depends(auth.get_user_data_dependency()), db: AsyncSession = Depends(get_db)):
    user_id = int(user_data["sub"])
    service = PageService(db)
    return await service.moderator_pages(moderator_id)

@router.delete("/{page_id}/moderator/{moderator_id}", response_model=StandardResponse[PageResponse])
@autowrap
async def delete_moderator(page_id: int, moderator_id: int, user_data = Depends(auth.get_user_data_dependency()), db: AsyncSession = Depends(get_db)):
    user_id = int(user_data["sub"])
    service = PageService(db)
    return await service.delete_moderator(page_id, moderator_id, user_id)

