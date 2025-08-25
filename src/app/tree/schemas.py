from pydantic import BaseModel, Field
from typing import Optional



class BaseTree(BaseModel):
    id: int = Field(..., description="ID дерева", example=1)
    name: str = Field(..., description="Название дерева", example="Жарты")

    class Config:
        from_attributes = True


class TreeResponse(BaseTree):
    id: int = Field(..., description="ID дерева", example=1)
    name: str = Field(..., description="Название дерева", example="Жарты")
    birth: Optional[str] = Field(None, description="Дата рождения", example="1990-01-01")
    death: Optional[str] = Field(None, description="Дата смерти", example="2020-01-01")
    bio: Optional[str] = Field(None, description="Биография", example="Биография")
    
    mini_icon: Optional[str] = Field(None, description="Миниатюра", example="https://example.com/mini_icon.jpg")
    main_icon: Optional[str] = Field(None, description="Главная иконка", example="https://example.com/main_icon.jpg")
    
    created_by: Optional[int] = Field(None, description="ID создателя", example=1)
    updated_by: Optional[int] = Field(None, description="ID обновляющего", example=1)


class SearchTree(BaseTree):
    name: str
    parent_id: int