from fastapi import HTTPException
from src.app.family.models import Family
from src.app.family.schemas import *
from src.app.tariff.models import Tariff, UserTariff

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import Optional

class FamilyService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def _set_partners(self, husband_id: int, wife_id: int) -> bool:
        husband = await self.db.execute(select(Family).where(Family.id == husband_id))
        husband = husband.scalars().first()
        wife = await self.db.execute(select(Family).where(Family.id == wife_id))
        wife = wife.scalars().first()
        if husband and wife:
            if husband.partners_id is None:
                husband.partners_id = []
            if wife.partners_id is None:
                wife.partners_id = []
                
            if wife_id not in husband.partners_id:
                husband.partners_id = husband.partners_id + [wife_id]
            if husband_id not in wife.partners_id:
                wife.partners_id = wife.partners_id + [husband_id]

            await self.db.flush()
            return True
        return False

    async def _remove_partner(self, partner_id: int) -> bool:
        try:
            # Находим всех, у кого этот партнер в списке
            query = select(Family).where(Family.partners_id.any(partner_id))
            partners = await self.db.execute(query)
            partners = partners.scalars().all()

            if not partners:
                return True  # Если ни у кого нет этого партнера, считаем что всё ок

            # Удаляем ID партнера из списков всех его партнеров
            for partner in partners:
                if partner.partners_id is not None:
                    partner.partners_id = [pid for pid in partner.partners_id if pid != partner_id]

            await self.db.flush()
            await self.db.commit()
            
            return True
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Ошибка при удалении партнера из списков: {str(e)}")

    async def _set_father(self, node_id: int, father_id: int) -> bool:
        node = await self.db.execute(select(Family).where(Family.id == node_id))
        node = node.scalars().first()
        if node:
            node.father_id = father_id
            await self.db.flush()
            return True
        return False
    
    async def _set_mother(self, node_id: int, mother_id: int) -> bool:
        node = await self.db.execute(select(Family).where(Family.id == node_id))
        node = node.scalars().first()
        if node:
            node.mother_id = mother_id
            await self.db.flush()
            return True
        return False

    async def create_node(
            self, 
            user_id: int,
            node: FamilyCreate,
            father_id: int = None,
            mother_id: int = None,
            partner_id: int = None,
            ) -> FamilyResponse:
        try:
            # Проверка существования связанных узлов
            if father_id:
                father = await self.db.execute(select(Family).where(Family.id == father_id))
                father = father.scalars().first()
                if not father:
                    raise HTTPException(status_code=404, detail="Отец не найден")
            
            if mother_id:
                mother = await self.db.execute(select(Family).where(Family.id == mother_id))
                mother = mother.scalars().first()
                if not mother:
                    raise HTTPException(status_code=404, detail="Мать не найдена")
            
            if partner_id:
                partner = await self.db.execute(select(Family).where(Family.id == partner_id))
                partner = partner.scalars().first()
                if not partner:
                    raise HTTPException(status_code=404, detail="Партнер не найден")

            new_node = Family(
                user_id=user_id,
                full_name=node.full_name,
                date_of_birth=node.date_of_birth,
                is_alive=node.is_alive,
                death_date=node.death_date,
                bio=node.bio,
                sex=node.sex,
                img='https://cdn.atatek.kz/family/default.png',
            )
            self.db.add(new_node)
            await self.db.flush()

            # Валидация пола при установке связей
            if father_id and node.sex.lower() == 'male':
                raise HTTPException(status_code=400, detail="Нельзя установить отца для мужчины")
            if mother_id and node.sex.lower() == 'female':
                raise HTTPException(status_code=400, detail="Нельзя установить мать для женщины")

            if father_id:
                await self._set_father(new_node.id, father_id)
            if mother_id:
                await self._set_mother(new_node.id, mother_id)
            if partner_id:
                await self._set_partners(new_node.id, partner_id)
            await self.db.commit()
            await self.db.refresh(new_node)
            return FamilyResponse(
                id=new_node.id,
                full_name=new_node.full_name,
                date_of_birth=new_node.date_of_birth,
                is_alive=new_node.is_alive,
                death_date=new_node.death_date,
                bio=new_node.bio,
                sex=new_node.sex,
                fid=new_node.father_id,
                mid=new_node.mother_id,
                pids=new_node.partners_id,
                user_id=new_node.user_id,
            ).model_dump()
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Ошибка при создании узла: {str(e)}")

    async def get_family_tree(self, user_id: int) -> FamilyTree:
        try:
            # Получение всех узлов семьи для данного пользователя
            query = select(Family).where(Family.user_id == user_id, Family.is_deleted == False).order_by(Family.id)
            nodes = await self.db.execute(query)
            nodes = nodes.scalars().all()
            return FamilyTree(
                nodes=[
                    FamilyResponse(
                        id=node.id,
                        full_name=node.full_name,
                        date_of_birth=node.date_of_birth,
                        is_alive=node.is_alive,
                        death_date=node.death_date,
                        bio=node.bio,
                        sex=node.sex,
                        fid=node.father_id,
                        mid=node.mother_id,
                        pids=node.partners_id,
                        user_id=node.user_id,
                    ).model_dump() 
                    for node in nodes]
            ).model_dump()
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Ошибка при получении дерева семьи: {str(e)}")

    async def delete_user(self, user_id: int, node_id: int) -> dict:
        try:
            node = await self.db.execute(select(Family).where(Family.id == node_id))
            node = node.scalars().first()
            if not node:
                raise HTTPException(status_code=404, detail="Узел не найден")
            
            node.is_deleted = True

            remove_partner = await self._remove_partner(node_id)
            if remove_partner:
                await self.db.commit()
                return {"message": "Партнер успешно удален"}
            else:
                raise HTTPException(status_code=400, detail="Ошибка при удалении партнера")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Ошибка при удалении пользователя: {str(e)}")

    async def update_node(self, node_id: int, node: UpdateNode) -> FamilyResponse:
        try:
            node_base = await self.db.execute(select(Family).where(Family.id == node_id))
            node_base = node_base.scalars().first()
            if not node_base:
                raise HTTPException(status_code=404, detail="Узел не найден")
            
            if node.full_name:
                node.full_name = node_base.full_name
            if node.date_of_birth:
                node.date_of_birth = node_base.date_of_birth
            if node.is_alive:
                node.is_alive = node_base.is_alive
            if node.death_date:
                node.death_date = node_base.death_date
            if node.bio:
                node.bio = node_base.bio

            await self.db.commit()
            await self.db.refresh(node)
            return FamilyResponse(
                id=node.id,
                full_name=node.full_name,
                date_of_birth=node.date_of_birth,
                is_alive=node.is_alive,
                death_date=node.death_date,
                bio=node.bio,
                sex=node.sex,
                fid=node.father_id,
                mid=node.mother_id,
                pids=node.partners_id,
                user_id=node.user_id,
            ).model_dump()
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Ошибка при обновлении узла: {str(e)}")
