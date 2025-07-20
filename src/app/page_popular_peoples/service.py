from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from src.app.page_popular_peoples.models import PagePopularPeoples
from src.app.page_popular_peoples.schemas import CreatePagePopularPeople, PagePopularPeopleResponse
from datetime import datetime

class PagePopularPeoplesService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_popular_person(self, person_data: CreatePagePopularPeople) -> PagePopularPeopleResponse:
        person = PagePopularPeoples(
            page_id=person_data.page_id,
            full_name=person_data.full_name,
            date_of_birth=datetime.fromisoformat(person_data.date_of_birth),
            death_date=datetime.fromisoformat(person_data.death_date) if person_data.death_date else None,
            bio=person_data.bio,
            image=person_data.image
        )
        self.db.add(person)
        await self.db.commit()
        await self.db.refresh(person)
        return PagePopularPeopleResponse(
            id=person.id,
            page_id=person.page_id,
            full_name=person.full_name,
            date_of_birth=person.date_of_birth.isoformat(),
            death_date=person.death_date.isoformat() if person.death_date else None,
            bio=person.bio,
            image=person.image
        ).model_dump()

    async def get_popular_person_by_id(self, person_id: int) -> PagePopularPeopleResponse:
        query = select(PagePopularPeoples).where(PagePopularPeoples.id == person_id)
        result = await self.db.execute(query)
        person = result.scalar_one_or_none()
        if not person:
            raise Exception("Popular person not found")
        return PagePopularPeopleResponse(
            id=person.id,
            page_id=person.page_id,
            full_name=person.full_name,
            date_of_birth=person.date_of_birth.isoformat(),
            death_date=person.death_date.isoformat() if person.death_date else None,
            bio=person.bio,
            image=person.image
        ).model_dump()

    async def get_popular_peoples_by_page_id(self, page_id: int) -> list[PagePopularPeopleResponse]:
        query = select(PagePopularPeoples).where(PagePopularPeoples.page_id == page_id)
        result = await self.db.execute(query)
        peoples = result.scalars().all()
        return [
            PagePopularPeopleResponse(
                id=person.id,
                page_id=person.page_id,
                full_name=person.full_name,
                date_of_birth=person.date_of_birth.isoformat(),
                death_date=person.death_date.isoformat() if person.death_date else None,
                bio=person.bio,
                image=person.image
            ).model_dump() for person in peoples
        ]

    async def update_popular_person(self, person_id: int, person_data: CreatePagePopularPeople) -> PagePopularPeopleResponse:
        query = update(PagePopularPeoples).where(PagePopularPeoples.id == person_id).values(
            full_name=person_data.full_name,
            date_of_birth=datetime.fromisoformat(person_data.date_of_birth),
            death_date=datetime.fromisoformat(person_data.death_date) if person_data.death_date else None,
            bio=person_data.bio,
            image=person_data.image
        )
        await self.db.execute(query)
        await self.db.commit()
        return await self.get_popular_person_by_id(person_id)

    async def delete_popular_person(self, person_id: int) -> bool:
        query = delete(PagePopularPeoples).where(PagePopularPeoples.id == person_id)
        await self.db.execute(query)
        await self.db.commit()
        return True 