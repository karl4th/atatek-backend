from datetime import datetime

from sqlalchemy import Text, func, Integer, String, ARRAY
from sqlalchemy.orm import Mapped, mapped_column

from src.app.db.core import Base
from enum import Enum

class Gender(Enum):
    M = 'M'
    F = 'F'

class Relation(Enum):
    father = 'father'
    mother = 'mother'
    children = 'children'
    spouses = 'spouses'

class Aulet(Base):
    __tablename__ = 'aulet'

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, nullable=False)

    first_name: Mapped[str] = mapped_column(nullable=False)
    last_name: Mapped[str] = mapped_column(nullable=False)
   
    gender: Mapped[Gender] = mapped_column(nullable=False)

    birthday: Mapped[str] = mapped_column(nullable=False)
    death_date: Mapped[str] = mapped_column(nullable=True)

    avatar: Mapped[str] = mapped_column(String, nullable=True)

    created_at: Mapped[datetime] = mapped_column(nullable=True, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(nullable=True, server_default=func.now(), server_onupdate=func.now())

    is_deleted: Mapped[bool] = mapped_column(nullable=True, default=False)

class AuletRelation(Base):
    __tablename__ = 'aulet_relation'
    
    id: Mapped[int] = mapped_column(primary_key=True)

    type: Mapped[Relation] = mapped_column(nullable=False)

    node_id: Mapped[int] = mapped_column(Integer, nullable=False)
    related_node_id: Mapped[int] = mapped_column(Integer, nullable=False)

    created_at: Mapped[datetime] = mapped_column(nullable=True, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(nullable=True, server_default=func.now(), server_onupdate=func.now())
    
    
    
    