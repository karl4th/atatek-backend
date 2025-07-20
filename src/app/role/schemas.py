from pydantic import BaseModel, Field


class BaseRole(BaseModel):
    id: int = Field(..., example=1)
    name: str = Field(..., example="admin")
    description: str = Field(..., example="Администратор")
