from src.app.tree.models import Tree
from src.app.auth.models import User
from src.app.pages.models import *
from src.app.pages.schemas import *
from src.app.role.service import RoleService
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException
from sqlalchemy import select


class PageService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.role_service = RoleService(db)

    async def create_page(self, page: CreatePage, user_id: int) -> PageResponse:
        user_role = await self.role_service.get_user_role(user_id)
        if user_role != 3:
            raise HTTPException(status_code=403, detail="У вас нет прав на создание страниц")
        try:
            existing_page = await self.db.execute(select(Page).where(Page.tree_id == page.tree_id))
            if existing_page.scalar_one_or_none():
                raise HTTPException(status_code=400, detail="Страница с таким деревом уже существует")
            
            tree_data = await self.db.execute(select(Tree).where(Tree.id == page.tree_id))
            tree_data = tree_data.scalars().first()
            if not tree_data:
                raise HTTPException(status_code=400, detail="Запись с таким ID не найдена")
            
            tree=BaseTree(id=tree_data.id, name=tree_data.name).model_dump()
            
            new_page = Page(
                title=page.title,
                tree_id=page.tree_id,
                bread1=page.bread1,
                bread2=page.bread2,
                bread3=page.bread3,
                main_gen=page.main_gen,
                main_gen_child=page.main_gen_child,
            )
            self.db.add(new_page)
            await self.db.commit()
            await self.db.refresh(new_page)

            

            return PageResponse(
                id=new_page.id,
                title=new_page.title,
                tree=tree,
                bread1=new_page.bread1,
                bread2=new_page.bread2,
                bread3=new_page.bread3,
                main_gen=new_page.main_gen,
                main_gen_child=new_page.main_gen_child,
                moderators=None,
            ).model_dump()
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))

    async def get_page_by_id(self, page_id: int) -> PageResponse:
        try:
            page = await self.db.execute(select(Page).where(Page.id == page_id))
            result = page.scalars().first()
            if not result:
                raise HTTPException(status_code=404, detail="Страница не найдена")
            
            moderators = await self.db.execute(
                select(User)
                .select_from(User)
                .join(PageModerator, User.id == PageModerator.user_id)
                .where(PageModerator.page_id == page_id)
            )
            moderators_list = [
                BaseUser(
                    id=moderator.id, 
                    first_name=moderator.first_name, 
                    last_name=moderator.last_name, 
                    phone=moderator.phone
                    ).model_dump()
                    for moderator in moderators.scalars().all()
                ]
            
            tree_data = await self.db.execute(select(Tree).where(Tree.id == result.tree_id))
            tree_data = tree_data.scalars().first()
            if not tree_data:
                raise HTTPException(status_code=400, detail="Запись с таким ID не найдена")

            return PageResponse(
                id=result.id,
                title=result.title,
                tree=BaseTree(id=tree_data.id, name=tree_data.name).model_dump(),
                bread1=result.bread1,
                bread2=result.bread2,
                bread3=result.bread3,
                main_gen=result.main_gen,
                main_gen_child=result.main_gen_child,
                moderators=moderators_list,
            ).model_dump()
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))

    async def set_moderator(self, page_id: int, moderator_id: int, user_id: int) -> PageResponse:
        try:
            user_role = await self.role_service.get_user_role(user_id)
            if user_role != 3:
                raise HTTPException(status_code=403, detail="У вас нет прав на создание страниц")
            
            page = await self.db.execute(select(Page).where(Page.id == page_id))
            result = page.scalars().first()
            if not result:
                raise HTTPException(status_code=404, detail="Страница не найдена")
            
            existing_moderator = await self.db.execute(
                select(PageModerator).where(
                    PageModerator.page_id == page_id, 
                    PageModerator.user_id == moderator_id
                )
            )
            if existing_moderator.scalar_one_or_none():
                raise HTTPException(status_code=400, detail="Этот пользователь уже является модератором")
            
            new_moderator = PageModerator(
                page_id=page_id,
                user_id=moderator_id,
            )
            self.db.add(new_moderator)
            await self.db.commit()
            await self.db.refresh(new_moderator)

            return await self.get_page_by_id(page_id)
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))

    async def moderator_pages(self, user_id: int) -> PageResponseList:
        try:
            pages = await self.db.execute(
                select(Page)
                .select_from(Page)
                .join(PageModerator, Page.id == PageModerator.page_id)
                .where(PageModerator.user_id == user_id)
            )
            result = pages.scalars().all()
            if not result:
                raise HTTPException(status_code=404, detail="Страницы не найдены")
            
            pages_response = []
            for page in result:
                moderators = await self.db.execute(
                    select(User)
                    .select_from(PageModerator)
                    .join(User, PageModerator.user_id == User.id)
                    .where(PageModerator.page_id == page.id)
                )
                moderators_list = [
                    BaseUser(
                        id=moderator.id, 
                        first_name=moderator.first_name, 
                        last_name=moderator.last_name, 
                        phone=moderator.phone
                    ).model_dump()
                    for moderator in moderators.scalars().all()
                ]
                
                tree_data = await self.db.execute(select(Tree).where(Tree.id == page.tree_id))
                tree = tree_data.scalars().first()
                
                pages_response.append(
                    PageResponse(
                        id=page.id,
                        title=page.title,
                        tree=BaseTree(id=tree.id, name=tree.name).model_dump(),
                        bread1=page.bread1,
                        bread2=page.bread2,
                        bread3=page.bread3,
                        main_gen=page.main_gen,
                        main_gen_child=page.main_gen_child,
                        moderators=moderators_list,
                    ).model_dump()
                )
            
            return PageResponseList(pages=pages_response).model_dump()
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e)) 
    
    async def delete_moderator(self, page_id: int, moderator_id: int, user_id: int) -> PageResponse:
        try:
            user_role = await self.role_service.get_user_role(user_id)
            if user_role != 3:
                raise HTTPException(status_code=403, detail="У вас нет прав на удаление модераторов")
            
            page = await self.db.execute(select(Page).where(Page.id == page_id))
            result = page.scalars().first()
            if not result:
                raise HTTPException(status_code=404, detail="Страница не найдена")
            
            moderator = await self.db.execute(select(PageModerator).where(PageModerator.page_id == page_id, PageModerator.user_id == moderator_id))
            moderator = moderator.scalars().first()
            if not moderator:
                raise HTTPException(status_code=404, detail="Модератор не найден")
            
            await self.db.delete(moderator)
            await self.db.commit()

            return await self.get_page_by_id(page_id)
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))

    async def get_pages_from_main_juz(self, main_juz_id: int, user_id: int) -> PageResponseList:
        try: 
            page = await self.db.execute(select(Page).where(Page.main_gen_child == main_juz_id))
            result = page.scalars().all()

            if not result:
                raise HTTPException(status_code=404, detail="Ничего не найдено")
            
            pages_response = []
            for page in result:
                tree_data = await self.db.execute(select(Tree).where(Tree.id == page.tree_id))
                tree = tree_data.scalars().first()
                if not tree:
                    raise HTTPException(status_code=400, detail="Запись с таким ID не найдена")
                
                pages_response.append(
                    PageResponse(
                        id=page.id,
                        title=page.title,
                        tree=BaseTree(id=tree.id, name=tree.name).model_dump(),
                        bread1=page.bread1,
                        bread2=page.bread2,
                        bread3=page.bread3,
                        main_gen=page.main_gen,
                        main_gen_child=page.main_gen_child,
                        moderators=None,
                    ).model_dump()
                )
            
            return PageResponseList(pages=pages_response).model_dump()
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))