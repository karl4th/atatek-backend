from pydantic import BaseModel, Field

class BaseTariff(BaseModel):
    id: int = Field(..., example=1)
    name: str = Field(..., example="admin")
    t_add_child: int = Field(..., example=1)
    t_edit_child: int = Field(..., example=1)
    t_family_count: int = Field(..., example=1)
