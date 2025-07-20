import re
from typing import Optional
                                                
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from src.app.role.models import *
from src.app.role.schemas import *


class RoleService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def link_user(self, user_id: int, role: int = None):
        try:
            role_id = role if role is not None else 1
            
            # Проверяем, не существует ли уже связь
            existing_link = await self.db.execute(
                select(UserRole).where(
                    UserRole.user_id == user_id,
                    UserRole.role_id == role_id
                )
            )
            if existing_link.scalar_one_or_none():
                return {"message": "Пользователь уже имеет эту роль"}

            # Создаем новую связь
            user_role = UserRole(user_id=user_id, role_id=role_id)
            self.db.add(user_role)
            await self.db.commit()
            return {"message": "Пользователь успешно привязан к роли"}

        except SQLAlchemyError as e:
            await self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Ошибка при привязке роли к пользователю"
            )

    async def get_user_role(self, user_id: int):
        try:
            user_role = await self.db.execute(select(UserRole).where(UserRole.user_id == user_id))
            result = user_role.scalars().first()
            if not result:
                raise HTTPException(status_code=404, detail="Роль не найдена")
            return result.role_id
        except SQLAlchemyError as e:
            raise HTTPException(status_code=400, detail=str(e))
