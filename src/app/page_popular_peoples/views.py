from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from src.app.config.response import StandardResponse, autowrap
from src.app.db.core import get_db
from src.app.page_popular_peoples.schemas import *
from src.app.page_popular_peoples.service import PagePopularPeoplesService
from src.app.config.auth import auth

router = APIRouter()

@router.post("/create", response_model=StandardResponse[PagePopularPeopleResponse])
@autowrap
async def create_popular_person(
    person_data: CreatePagePopularPeople,
    user_data = Depends(auth.get_user_data_dependency()),
    db: AsyncSession = Depends(get_db)
):
    service = PagePopularPeoplesService(db)
    person = await service.create_popular_person(person_data)
    return person

@router.get("/{person_id}", response_model=StandardResponse[PagePopularPeopleResponse])
@autowrap
async def get_popular_person(
    person_id: int,
    db: AsyncSession = Depends(get_db)
):
    service = PagePopularPeoplesService(db)
    person = await service.get_popular_person_by_id(person_id)
    return person

@router.get("/page/{page_id}", response_model=StandardResponse[list[PagePopularPeopleResponse]])
@autowrap
async def get_popular_peoples_by_page(
    page_id: int,
    db: AsyncSession = Depends(get_db)
):
    service = PagePopularPeoplesService(db)
    peoples = await service.get_popular_peoples_by_page_id(page_id)
    return peoples

@router.put("/{person_id}", response_model=StandardResponse[PagePopularPeopleResponse])
@autowrap
async def update_popular_person(
    person_id: int,
    person_data: CreatePagePopularPeople,
    user_data = Depends(auth.get_user_data_dependency()),
    db: AsyncSession = Depends(get_db)
):
    service = PagePopularPeoplesService(db)
    person = await service.update_popular_person(person_id, person_data)
    return person

@router.delete("/{person_id}", response_model=StandardResponse[bool])
@autowrap
async def delete_popular_person(
    person_id: int,
    user_data = Depends(auth.get_user_data_dependency()),
    db: AsyncSession = Depends(get_db)
):
    service = PagePopularPeoplesService(db)
    result = await service.delete_popular_person(person_id)
    return result 