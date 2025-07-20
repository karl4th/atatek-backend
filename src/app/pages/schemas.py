from pydantic import BaseModel, Field
from typing import Optional
from src.app.auth.schemas import BaseUser
from src.app.tree.schemas import BaseTree


class CreatePage(BaseModel):
    title: str = Field(..., description="Название страницы", example="Жарты")
    tree_id: int = Field(..., description="ID дерева", example=25)

    bread1: str = Field(..., description="1 поколение", example="alban")
    bread2: str = Field(..., description="2 поколение", example="sary")
    bread3: str = Field(..., description="3 поколение", example="zharty")

    main_gen: int = Field(..., description="ID жуза", example=2)
    main_gen_child: int = Field(..., description="ID рода внутри жуза", example=15)

class CreatePageModerator(BaseModel):
    page_id: int = Field(..., description="ID страницы", example=1)
    user_id: int = Field(..., description="ID пользователя", example=1)

class UpdatePage(BaseModel):
    title: Optional[str] = Field(None, description="Название страницы", example="Жарты")
    tree_id: Optional[int] = Field(None, description="ID дерева", example=25)

    bread1: Optional[str] = Field(None, description="1 поколение", example="alban")
    bread2: Optional[str] = Field(None, description="2 поколение", example="sary")
    bread3: Optional[str] = Field(None, description="3 поколение", example="zharty")

    main_gen: Optional[int] = Field(None, description="ID жуза", example=2)
    main_gen_child: Optional[int] = Field(None, description="ID рода внутри жуза", example=15)

class UpdatePageModerator(BaseModel):
    page_id: Optional[int] = Field(None, description="ID страницы", example=1)
    user_id: Optional[int] = Field(None, description="ID пользователя", example=1)


class ModeratorList(BaseModel):
    moderators: list[BaseUser] = Field(..., description="Список модераторов")

class PageResponse(BaseModel):
    id: int = Field(..., description="ID страницы", example=1)
    title: str = Field(..., description="Название страницы", example="Жарты")
    tree: BaseTree = Field(..., description="Дерево")

    bread1: str = Field(..., description="1 поколение", example="alban")
    bread2: str = Field(..., description="2 поколение", example="sary")
    bread3: str = Field(..., description="3 поколение", example="zharty")

    main_gen: int = Field(..., description="ID жуза", example=2)
    main_gen_child: int = Field(..., description="ID рода внутри жуза", example=15)
    moderators: Optional[list[BaseUser]] = Field(None, description="Список модераторов")

    class Config:
        from_attributes = True

class PageResponseList(BaseModel):
    pages: list[PageResponse] = Field(..., description="Список страниц")
