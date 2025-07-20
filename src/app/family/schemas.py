from pydantic import BaseModel, Field
from typing import Optional


class FamilyCreate(BaseModel):
    full_name: str = Field(..., description="Имя и фамилия")
    date_of_birth: str = Field(..., description="Дата рождения")
    is_alive: bool = Field(..., description="Жив ли человек")
    death_date: Optional[str] = Field(None, description="Дата смерти")
    bio: Optional[str] = Field(None, description="Биография")
    sex: str = Field(..., description="Пол")

 
class FamilyResponse(BaseModel):
    id: int = Field(..., example=1)
    full_name: str = Field(..., example="Иван Иванов")
    date_of_birth: str = Field(..., example="1990-01-01")
    is_alive: bool = Field(..., example=True)
    death_date: Optional[str] = Field(None, example=None)
    bio: Optional[str] = Field(None, example=None)
    sex: str = Field(..., example="man")
    fid: Optional[int] = Field(None, example=None)
    mid: Optional[int] = Field(None, example=None)
    pids: Optional[list[int]] = Field(None, example=[1, 2])
    user_id: int = Field(..., example=1)

    class Config:
        from_attributes = True


class FamilyTree(BaseModel):
    nodes: list[FamilyResponse]

    class Config:
        from_attributes = True

class UpdateNode(BaseModel):
    full_name: Optional[str] = Field(None, example="Иван Иванов")
    date_of_birth: Optional[str] = Field(None, example="1990-01-01")
    is_alive: Optional[bool] = Field(None, example=True)
    death_date: Optional[str] = Field(None, example=None)
    bio: Optional[str] = Field(None, example=None)

