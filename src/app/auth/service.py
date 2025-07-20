import re
from typing import Optional

from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from src.app.pages.models import UserPage, Page
from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from src.app.auth.models import User
from src.app.auth.schemas import *
from src.app.role.models import UserRole, Role
from src.app.address.models import UserAddress, Address
from src.app.tariff.models import UserTariff, Tariff
from src.app.aulet.models import Aulet
from src.app.tree.models import Tree

# Инициализация Argon2 хешера
password_hasher = PasswordHasher()


def hash_password(password: str) -> str:
    """Хеширование пароля с использованием Argon2"""
    return password_hasher.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Проверка пароля с использованием Argon2"""
    try:
        return password_hasher.verify(hashed_password, plain_password)
    except VerifyMismatchError:
        return False


class UsersService:
    def __init__(self, db: AsyncSession):
        self.db = db

    def _validate_phone(self, phone: str) -> bool:
        """Валидация номера телефона"""
        # Базовая проверка: 10-15 цифр
        return bool(re.match(r'^\+?[0-9]{10,15}$', phone))

    def _validate_password(self, password: str) -> bool:
        """Проверка пароля на минимальную сложность"""
        # Минимум 8 символов
        return len(password) >= 8

    async def _get_user_by_phone(self, phone: str):
        """Получение пользователя по номеру телефона"""
        query = select(User).where(User.phone == phone)
        result = await self.db.execute(query)
        return result.scalars().first()

    async def _get_tariff_and_role(self, user_id: int):
        try:
            # Получаем роль пользователя с JOIN
            role_query = (
                select(Role)
                .join(UserRole, Role.id == UserRole.role_id)
                .where(UserRole.user_id == user_id)
            )
            role_result = await self.db.execute(role_query)
            role_data = role_result.scalars().first()
            
            if not role_data:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Роль пользователя не найдена"
                )

            # Получаем тариф пользователя с JOIN
            tariff_query = (
                select(
                    Tariff.id,
                    Tariff.name,
                    Tariff.price,
                    UserTariff.t_add_child,
                    UserTariff.t_edit_child,
                    UserTariff.t_family_count
                )
                .join(UserTariff, Tariff.id == UserTariff.tariff_id)
                .where(UserTariff.user_id == user_id)
            )
            tariff_result = await self.db.execute(tariff_query)
            tariff_data = tariff_result.first()
            
            if not tariff_data:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Тариф пользователя не найден"
                )

            return tariff_data, role_data
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Ошибка при получении данных пользователя: {str(e)}"
            )

    async def create_new_user(self, user_data: CreateUser):
        # Валидация данных
        if not self._validate_phone(user_data.phone):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Неверный формат номера телефона"
            )

        if not self._validate_password(user_data.password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Пароль должен содержать минимум 8 символов"
            )

        # Проверка на существующего пользователя
        existing_user = await self._get_user_by_phone(user_data.phone)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Пользователь с номером {user_data.phone} уже существует"
            )

        try:
            # Создание пользователя
            new_user = User(
                first_name=user_data.first_name,
                last_name=user_data.last_name,
                middle_name=user_data.middle_name,                                                              
                phone=user_data.phone,
                password=hash_password(user_data.password),
                is_active=True,
                is_verified=False,
                is_deleted=False,
                is_banned=False,
            )
            self.db.add(new_user)
            await self.db.flush()

            # Создание роли пользователя
            role = UserRole(user_id=new_user.id, role_id=1)
            self.db.add(role)

            # Создание тарифа пользователя
            tariff = UserTariff(user_id=new_user.id, tariff_id=1)
            self.db.add(tariff)

            await self.db.commit()
            await self.db.refresh(new_user)
            return UserResponse(
                id=new_user.id,
                first_name=new_user.first_name,
                last_name=new_user.last_name,
                middle_name=new_user.middle_name if new_user.middle_name else None,
                phone=new_user.phone,
            ).model_dump()

        except HTTPException:
            await self.db.rollback()
            raise
        except Exception as e:
            await self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Ошибка при создании пользователя: {str(e)}"
            )

    async def login_user(self, user_data: LoginUser):
        try:
            # Проверка пользователя
            user = await self._get_user_by_phone(user_data.phone)
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Пользователь с номером {user_data.phone} не найден"
                )

            # Проверка на блокировку
            if user.is_banned:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Пользователь заблокирован"
                )

            # Проверка активации
            if not user.is_active:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Пользователь не активирован"
                )

            # Проверка пароля
            if not verify_password(user_data.password, user.password):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Неверный пароль"
                )

            tariff, role = await self._get_tariff_and_role(user.id)
            return UserResponse(
                id=user.id,
                first_name=user.first_name,
                last_name=user.last_name,
                middle_name=user.middle_name,
                phone=user.phone,
                role=BaseRole(id=role.id, name=role.name, description=role.description).model_dump(),
                tariff=BaseTariff(
                    id=tariff.id, 
                    name=tariff.name, 
                    price=tariff.price, 
                    t_add_child=tariff.t_add_child, 
                    t_edit_child=tariff.t_edit_child, 
                    t_family_count=tariff.t_family_count
                ).model_dump(),
            ).model_dump()
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Ошибка при авторизации: {e}"
            )

    async def get_user_by_id(self, user_id: int):
        """Получение пользователя по ID"""
        try:
            result = await self.db.execute(select(User).where(User.id == user_id))
            user = result.scalars().first()

            if not user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Пользователь с ID {user_id} не найден"
                )
            tariff, role = await self._get_tariff_and_role(user.id)
            return UserResponse(
                id=user.id,
                first_name=user.first_name,
                last_name=user.last_name,
                middle_name=user.middle_name,
                phone=user.phone,
                role=BaseRole(id=role.id, name=role.name, description=role.description).model_dump(),
                tariff=BaseTariff(
                    id=tariff.id, 
                    name=tariff.name, 
                    price=tariff.price, 
                    t_add_child=tariff.t_add_child, 
                    t_edit_child=tariff.t_edit_child,
                    t_family_count=tariff.t_family_count
                ).model_dump(),
            ).model_dump()
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Ошибка при получении данных пользователя: {e}"
            )

    async def set_address(self, address: int, user_id: int):
        try:
            user_address = UserAddress(user_id=user_id, address_id=address) 
            self.db.add(user_address)
            await self.db.commit()
            return {"message": "Адрес успешно установлен"}
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Ошибка при установке адреса"
            )

    async def set_user_page(self, page_id: int, user_id: int) -> dict:
        try:
            existing_user_page = await self.db.execute(select(UserPage).where(UserPage.page_id == page_id, UserPage.user_id == user_id))
            if existing_user_page.scalar_one_or_none():
                raise HTTPException(status_code=400, detail="Страница уже привязана к пользователю")
            
            user_page = UserPage(
                page_id=page_id,
                user_id=user_id,
            )
            self.db.add(user_page)
            await self.db.commit()
            await self.db.refresh(user_page)

            return {
                "message": "Страница привязана к пользователю"
            }
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))

    async def get_profile(self, user_id: int) -> ProfileUser:
        try:
            user = await self.db.execute(select(User).where(User.id == user_id))
            user = user.scalars().first()

            address = await self.db.execute(
                select(Address)
                .select_from(UserAddress)
                .join(Address, Address.id == UserAddress.address_id)
                .where(UserAddress.user_id == user_id)
            )
            address = address.scalars().first()

            tree_added = await self.db.execute(select(Tree).where(Tree.created_by == user_id))
            tree_added = tree_added.scalars().all()

            tree_edited = await self.db.execute(select(Tree).where(Tree.updated_by == user_id))
            tree_edited = tree_edited.scalars().all()

            tree_family = await self.db.execute(select(Aulet).where(Aulet.user_id == user_id))
            tree_family = tree_family.scalars().all()
            
            return ProfileUser(
                id=user.id,
                first_name=user.first_name,
                last_name=user.last_name,
                middle_name=user.middle_name,
                phone=user.phone,
                created_at=user.created_at.isoformat() if user.created_at else None,
                address=address.display_name if address else None,
                all_added_nodes=len(tree_added),
                all_edited_nodes=len(tree_edited),
                all_family_nodes=len(tree_family),
            ).model_dump()
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))

    async def update_user(self, user_id: int, user_data: UpdateUser):
        try:
            user = await self.db.execute(select(User).where(User.id == user_id))
            user = user.scalars().first()
            
            if user_data.first_name:
                user.first_name = user_data.first_name
            if user_data.last_name:
                user.last_name = user_data.last_name
            if user_data.middle_name:
                user.middle_name = user_data.middle_name
            
            await self.db.commit()
            await self.db.refresh(user)

            return {
                "message": "Данные пользователя успешно обновлены"
            }
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))

    async def reset_password(self, user_id: int, user_data: ResetPassword):
        try:
            user = await self.db.execute(select(User).where(User.id == user_id))
            user = user.scalars().first()
            
            if not verify_password(user_data.password, user.password):
                raise HTTPException(status_code=400, detail="Неверный пароль")
            
            if user_data.new_password != user_data.confirm_password:
                raise HTTPException(status_code=400, detail="Пароли не совпадают")
            

            user.password = hash_password(user_data.new_password)
            await self.db.commit()
            await self.db.refresh(user)

            return {
                "message": "Пароль успешно сброшен"
            }
            
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))

    async def get_my_page(self, user_id: int):
        try:
            user_page = await self.db.execute(select(UserPage).where(UserPage.user_id == user_id))
            user_page = user_page.scalars().first()
            
            if not user_page:
                return []
            
            page = await self.db.execute(select(Page).where(Page.id == user_page.page_id))
            page = page.scalars().first()
            response = {
                "id": page.id,
                "title": page.title,
                "t_id": page.tree_id,
                "bread1": page.bread1,
                "bread2": page.bread2,
                "bread3": page.bread3,
                
            }
            return response if response else []
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))
            