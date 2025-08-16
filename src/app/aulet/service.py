from fastapi import HTTPException
from src.app.aulet.models import Aulet, AuletRelation, Relation, Gender
from src.app.aulet.schemas import *
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from sqlalchemy.orm import selectinload
from typing import Optional, List, Dict
from collections import defaultdict

class AuletService:
    def __init__(self, db: AsyncSession):
        self.db = db

    def _get_gender_value(self, gender):
        """Безопасное получение значения gender"""
        if isinstance(gender, Gender):
            return gender.value
        return str(gender) if gender else 'M'

    def _format_date(self, date_str: Optional[str]) -> Optional[str]:
        """Форматирует дату из строки в формат dd.mm.YYYY"""
        if date_str:
            try:
                date_obj = datetime.strptime(date_str, '%Y-%m-%d')
                return date_obj.strftime('%d.%m.%Y')
            except ValueError:
                # Если дата не в правильном формате, возвращаем None или исходную строку
                return date_str
        return None

    async def get_aulet_tree(self, user_id: int) -> List[dict]:
        """
        Получить дерево семьи в формате для family-chart библиотеки
        """
        # Получаем всех людей пользователя
        result = await self.db.execute(
            select(Aulet).where(
                and_(Aulet.user_id == user_id, Aulet.is_deleted == False)
            ).order_by(Aulet.birthday)
        )
        persons = result.scalars().all()
        
        if not persons:
            return []
        
        # Получаем все связи для этих людей
        person_ids = [person.id for person in persons]
        relations_result = await self.db.execute(
            select(AuletRelation).where(
                AuletRelation.node_id.in_(person_ids)
            )
        )
        relations = relations_result.scalars().all()
        
        # Группируем связи по person_id
        relations_by_person = defaultdict(lambda: {
            'spouses': [],
            'children': [],
            'father': None,
            'mother': None
        })
        
        for relation in relations:
            person_relations = relations_by_person[relation.node_id]
            
            if relation.type == Relation.spouses:
                person_relations['spouses'].append(str(relation.related_node_id))
            elif relation.type == Relation.children:
                person_relations['children'].append(str(relation.related_node_id))
            elif relation.type == Relation.father:
                person_relations['father'] = str(relation.related_node_id)
            elif relation.type == Relation.mother:
                person_relations['mother'] = str(relation.related_node_id)
        
        # Формируем результат в формате family-chart
        result_data = []
        for person in persons:
            person_relations = relations_by_person[person.id]
            
            # Формируем rels для family-chart - включаем все необходимые поля
            rels = {
                'spouses': person_relations['spouses'],
                'children': person_relations['children']
            }
            
            # Добавляем father и mother если они есть
            if person_relations['father']:
                rels['father'] = person_relations['father']
            if person_relations['mother']:
                rels['mother'] = person_relations['mother']
            
            # Добавляем родителей в children списки родителей
            if person_relations['father']:
                relations_by_person[int(person_relations['father'])]['children'].append(str(person.id))
            if person_relations['mother']:
                relations_by_person[int(person_relations['mother'])]['children'].append(str(person.id))
            
            person_data = {
                'id': str(person.id),
                'rels': rels,
                'data': {
                    'first name': person.first_name,
                    'last name': person.last_name,
                    'birthday': person.birthday.isoformat(),
                    'avatar': person.avatar if person.avatar else 'def-ava.png',
                    'gender': self._get_gender_value(person.gender)
                }
            }
            
            # Добавляем дату смерти если есть
            if person.death_date:
                person_data['data']['death_date'] = person.death_date.isoformat()
                
            result_data.append(person_data)
        
        # Убираем дубликаты в children списках
        for person_data in result_data:
            person_data['rels']['children'] = list(set(person_data['rels']['children']))
            person_data['rels']['spouses'] = list(set(person_data['rels']['spouses']))
        
        return result_data

    async def create_aulet_person(self, user_id: int, person: CreatePerson) -> dict:
        """
        Создать новую персону в семейном дереве
        """
        try:
            # Создаем новую персону
            gender_enum = Gender.M if person.data.gender == 'M' else Gender.F
            
            new_person = Aulet(
                user_id=user_id,
                first_name=person.data.first_name,
                last_name=person.data.last_name,
                gender=gender_enum,
                birthday=person.data.birthday,
                death_date=person.data.death_date,
                avatar=person.data.avatar if person.data.avatar else None,
                is_deleted=False
            )
            
            self.db.add(new_person)
            await self.db.flush()  # Получаем ID новой персоны
            
            # Создаем связи
            relations_to_add = []
            
            # Добавляем связи с супругами
            if person.rels.spouses:
                for spouse_id in person.rels.spouses:
                    # Связь от новой персоны к супругу
                    relations_to_add.append(AuletRelation(
                        type=Relation.spouses,
                        node_id=new_person.id,
                        related_node_id=spouse_id
                    ))
                    # Обратная связь от супруга к новой персоне
                    relations_to_add.append(AuletRelation(
                        type=Relation.spouses,
                        node_id=spouse_id,
                        related_node_id=new_person.id
                    ))
            
            # Добавляем связи с детьми
            if person.rels.children:
                for child_id in person.rels.children:
                    relations_to_add.append(AuletRelation(
                        type=Relation.children,
                        node_id=new_person.id,
                        related_node_id=child_id
                    ))
                    # Определяем связь ребенка с родителем (отец/мать)
                    parent_relation = Relation.father if person.data.gender == 'M' else Relation.mother
                    relations_to_add.append(AuletRelation(
                        type=parent_relation,
                        node_id=child_id,
                        related_node_id=new_person.id
                    ))
            
            # Добавляем связь с отцом
            if person.rels.father:
                relations_to_add.append(AuletRelation(
                    type=Relation.father,
                    node_id=new_person.id,
                    related_node_id=person.rels.father
                ))
                # Добавляем новую персону в children отца
                relations_to_add.append(AuletRelation(
                    type=Relation.children,
                    node_id=person.rels.father,
                    related_node_id=new_person.id
                ))
            
            # Добавляем связь с матерью
            if person.rels.mother:
                relations_to_add.append(AuletRelation(
                    type=Relation.mother,
                    node_id=new_person.id,
                    related_node_id=person.rels.mother
                ))
                # Добавляем новую персону в children матери
                relations_to_add.append(AuletRelation(
                    type=Relation.children,
                    node_id=person.rels.mother,
                    related_node_id=new_person.id
                ))
            
            # Добавляем все связи в базу
            if relations_to_add:
                self.db.add_all(relations_to_add)
            
            # Сохраняем данные до commit'а для избежания проблем с lazy loading
            person_id = new_person.id
            first_name = new_person.first_name
            last_name = new_person.last_name
            birthday = new_person.birthday.isoformat() if new_person.birthday else None
            avatar = new_person.avatar
            gender_value = self._get_gender_value(new_person.gender)
            
            await self.db.commit()
            
            # Возвращаем созданную персону в формате family-chart
            rels_data = {
                'spouses': [str(id) for id in (person.rels.spouses or [])],
                'children': [str(id) for id in (person.rels.children or [])]
            }
            
            # Добавляем father и mother если они есть
            if person.rels.father:
                rels_data['father'] = str(person.rels.father)
            if person.rels.mother:
                rels_data['mother'] = str(person.rels.mother)
            
            return {
                'id': str(person_id),
                'rels': rels_data,
                'data': {
                    'first name': first_name,
                    'last name': last_name,
                    'birthday': birthday,
                    'avatar': avatar if avatar else 'def-ava.png',
                    'gender': gender_value
                }
            }
            
        except Exception as e:
            await self.db.rollback()
            raise HTTPException(status_code=400, detail=f"Ошибка создания персоны: {str(e)}")

    async def update_aulet_person(self, user_id: int, person_update: UpdatePerson) -> dict:
        """
        Обновить персону в семейном дереве
        """
        try:
            # Получаем персону
            result = await self.db.execute(
                select(Aulet).where(
                    and_(
                        Aulet.id == person_update.person_id,
                        Aulet.user_id == user_id,
                        Aulet.is_deleted == False
                    )
                )
            )
            person = result.scalar_one_or_none()
            
            if not person:
                raise HTTPException(status_code=404, detail="Персона не найдена")
            
            # Обновляем данные персоны
            gender_enum = Gender.M if person_update.data.gender == 'M' else Gender.F
            
            person.first_name = person_update.data.first_name
            person.last_name = person_update.data.last_name
            person.gender = gender_enum
            person.birthday = person_update.data.birthday
            person.death_date = person_update.data.death_date
            person.avatar = person_update.data.avatar if person_update.data.avatar else None
            
            # Удаляем старые связи
            old_relations = await self.db.execute(
                select(AuletRelation).where(AuletRelation.node_id == person.id)
            )
            for old_relation in old_relations.scalars().all():
                await self.db.delete(old_relation)
            
            # Создаем новые связи (аналогично create_aulet_person)
            relations_to_add = []
            
            if person_update.rels.spouses:
                for spouse_id in person_update.rels.spouses:
                    relations_to_add.append(AuletRelation(
                        type=Relation.spouses,
                        node_id=person.id,
                        related_node_id=spouse_id
                    ))
            
            if person_update.rels.children:
                for child_id in person_update.rels.children:
                    relations_to_add.append(AuletRelation(
                        type=Relation.children,
                        node_id=person.id,
                        related_node_id=child_id
                    ))
            
            if person_update.rels.father:
                relations_to_add.append(AuletRelation(
                    type=Relation.father,
                    node_id=person.id,
                    related_node_id=person_update.rels.father
                ))
            
            if person_update.rels.mother:
                relations_to_add.append(AuletRelation(
                    type=Relation.mother,
                    node_id=person.id,
                    related_node_id=person_update.rels.mother
                ))
            
            if relations_to_add:
                self.db.add_all(relations_to_add)
            
            # Сохраняем данные до commit'а для избежания проблем с lazy loading
            person_id = person.id
            first_name = person.first_name
            last_name = person.last_name
            birthday = person.birthday
            avatar = person.avatar
            gender_value = self._get_gender_value(person.gender)
            
            await self.db.commit()
            
            # Возвращаем обновленную персону
            rels_data = {
                'spouses': [str(id) for id in (person_update.rels.spouses or [])],
                'children': [str(id) for id in (person_update.rels.children or [])]
            }
            
            # Добавляем father и mother если они есть
            if person_update.rels.father:
                rels_data['father'] = str(person_update.rels.father)
            if person_update.rels.mother:
                rels_data['mother'] = str(person_update.rels.mother)
            
            return {
                'id': str(person_id),
                'rels': rels_data,
                'data': {
                    'first name': first_name,
                    'last name': last_name,
                    'birthday': birthday.isoformat(),
                    'avatar': avatar if avatar else 'def-ava.png',
                    'gender': gender_value
                }
            }
            
        except HTTPException:
            raise
        except Exception as e:
            await self.db.rollback()
            raise HTTPException(status_code=400, detail=f"Ошибка обновления персоны: {str(e)}")

    async def delete_aulet_person(self, user_id: int, person_id: int) -> bool:
        """
        Удалить персону из семейного дерева (мягкое удаление)
        """
        try:
            result = await self.db.execute(
                select(Aulet).where(
                    and_(
                        Aulet.id == person_id,
                        Aulet.user_id == user_id,
                        Aulet.is_deleted == False
                    )
                )
            )
            person = result.scalar_one_or_none()
            
            if not person:
                raise HTTPException(status_code=404, detail="Персона не найдена")
            
            # Мягкое удаление
            person.is_deleted = True
            
            # Удаляем все связи с этой персоной
            relations_to_delete = await self.db.execute(
                select(AuletRelation).where(
                    (AuletRelation.node_id == person_id) | 
                    (AuletRelation.related_node_id == person_id)
                )
            )
            
            for relation in relations_to_delete.scalars().all():
                await self.db.delete(relation)
            
            await self.db.commit()
            return True
            
        except HTTPException:
            raise
        except Exception as e:
            await self.db.rollback()
            raise HTTPException(status_code=400, detail=f"Ошибка удаления персоны: {str(e)}")