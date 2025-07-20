from src.app.tariff.models import *
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException
from sqlalchemy import select

class TariffService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def _change_edit_count(self, user_id: int) -> bool:
        query = select(UserTariff).where(UserTariff.user_id == user_id)
        result = await self.db.execute(query)
        result = result.scalars().first()
        if not result:
            raise HTTPException(status_code=404, detail="Тариф не найден")
        
        if result.t_edit_child > 0:
            result.t_edit_child -= 1
            await self.db.flush()
            return True
        else:
            raise HTTPException(status_code=400, detail="Тикет не действует")
    
    async def _change_add_count(self, user_id: int, count: int = None) -> bool:
        try:
            query = select(UserTariff).where(UserTariff.user_id == user_id)
            result = await self.db.execute(query)
            result = result.scalars().first()
            if not result:
                raise HTTPException(status_code=404, detail="Тариф не найден")
            if result.t_add_child > 0:
                if count:
                    result.t_add_child -= count
                else:
                    result.t_add_child -= 1

            else: 
                raise HTTPException(status_code=400, detail="Тикет не действует")
            await self.db.flush()
            return True
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Ошибка при обновлении тарифа: {str(e)}")
        
        
