from pydantic import BaseModel, Field
from typing import Optional
from enum import Enum



class Rels(BaseModel):
    spouses: Optional[list[int]] = Field(None, description="ID супруга")
    children: Optional[list[int]] = Field(None, description="ID детей")
    father: Optional[int] = Field(None, description="ID отца")
    mother: Optional[int] = Field(None, description="ID матери")

    class Config:
        from_attributes = True

class PersonData(BaseModel):
    first_name: str = Field(..., description="Имя")
    last_name: str = Field(..., description="Фамилия")
    gender: str = Field(..., description="Пол")
    birthday: str = Field(..., description="Дата рождения")
    death_date: Optional[str] = Field(None, description="Дата смерти")
    avatar: Optional[str] = Field(None, description="Аватар")

    class Config:
        from_attributes = True

class AuletPerson(BaseModel):
    id: int = Field(..., description="ID")
    data: PersonData = Field(..., description="Данные")
    rels: Rels = Field(..., description="Связи")

    class Config:
        from_attributes = True

class AuletData(BaseModel):
    aulet: list[AuletPerson] = Field(..., description="Список людей")

    class Config:
        from_attributes = True


class CreatePerson(BaseModel):
    user_id: int = Field(..., description="ID пользователя")
    data: PersonData = Field(..., description="Данные")
    rels: Rels = Field(..., description="Связи")

    class Config:
        from_attributes = True

class UpdatePerson(BaseModel):
    person_id: int = Field(..., description="ID человека")
    data: PersonData = Field(..., description="Данные")
    rels: Rels = Field(..., description="Связи")

    class Config:
        from_attributes = True
