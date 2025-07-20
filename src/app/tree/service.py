from fastapi import HTTPException
import requests
import logging
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.app.auth.models import User
from src.app.tree.models import Tree
from src.app.role.models import UserRole


class TreeService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.base_url = 'https://tumalas.kz/wp-admin/admin-ajax.php?action=tuma_cached_childnew_get&nodeid=14&id='
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        }

    async def get_tree_on_api(self, id: int, parent_id: int):
        url = f'{self.base_url}&id={id}'
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            data = response.json()

            new_nodes = []
            for item in data:
                t_id = int(item['id'])

                # Проверяем, существует ли запись с таким t_id
                existing_node = await self.db.execute(select(Tree).where(Tree.t_id == t_id))
                if existing_node.scalars().first():
                    continue  # Пропускаем, если уже есть в БД

                new_node = Tree(
                    name=item['name'],
                    birth=item['birth_year'] if item['birth_year'] not in [None, 0] else None,
                    death=item['death_year'] if item['death_year'] not in [None, 0] else None,
                    parent_id=parent_id,
                    is_deleted=False,
                    t_id=t_id
                )

                self.db.add(new_node)
                new_nodes.append(new_node)

            if new_nodes:
                await self.db.commit()
            return new_nodes  # Возвращаем список добавленных узлов (может быть пустым)

        except Exception as e:
            logging.error(f"Ошибка при запросе дерева: {e}")
            return None  # Возвращаем None, если ошибка

    async def get_tree_on_db(self, node_id: int, user_id: int):
        result = await self.db.execute(select(Tree).where(Tree.id == node_id))
        node = result.scalars().first()
        if not node:
            raise HTTPException(status_code=404, detail='Node not found')

        # Проверяем, нет ли новых данных в API
        await self.get_tree_on_api(node.t_id, node_id)

        # После запроса к API делаем повторный запрос в БД (на случай обновлений)
        result = await self.db.execute(select(Tree).where(Tree.parent_id == node_id).order_by(Tree.id))
        childs = result.scalars().all()

        role = await self.db.execute(select(UserRole).where(UserRole.user_id == user_id))
        role = role.scalars().first()
        response = []
        if childs:
            for child in childs:
                if child.is_deleted:
                    continue

                response.append({
                    "id": child.id,
                    "name": child.name,
                    "birth": child.birth if child.birth else None,
                    "death": child.death if child.death else None,
                    "info": bool(child.bio),  # Более читабельная проверка
                    "untouchable": True if role.role_id >= 2 else False,
                    "mini_icon": child.mini_icon or None,  # Можно использовать `or`
                    "main_icon": child.main_icon or None,
                })
        return response

    async def delete_tree_on_page(self, node_id: int):
        result = await self.db.execute(select(Tree).where(Tree.id == node_id))
        node = result.scalars().first()
        if not node:
            raise HTTPException(status_code=404, detail='Node not found')
        node.is_deleted = True
        await self.db.commit()
        await self.db.refresh(node)
        return True

    async def restore_tree_on_page(self, node_id: int):
        result = await self.db.execute(select(Tree).where(Tree.id == node_id))
        node = result.scalars().first()
        if not node:
            raise HTTPException(status_code=404, detail='Node not found')
        node.is_deleted = False
        await self.db.commit()
        await self.db.refresh(node)
        return True


    async def get_tree_data(self, node_id: int):
        result = await self.db.execute(select(Tree).where(Tree.id == node_id))
        node = result.scalars().first()

        if not node:
            raise HTTPException(status_code=404, detail='Node not found')

        result = await self.db.execute(select(User).where(User.id == node.created_by))
        user = result.scalars().first()
        if not user:
            userD = None
        else:
            userD = {
                "id": user.id,
                "full_name": f'{user.first_name} {user.last_name}',
            }

        return {
            "id": node.id,
            "name": node.name,
            "mini_icon": node.mini_icon,
            "main_icon": node.main_icon,
            "birth": node.birth,
            "death": node.death,
            "bio": node.bio,
            "created_by": userD
        }