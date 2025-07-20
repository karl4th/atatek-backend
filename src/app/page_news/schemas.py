from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class CreatePageNews(BaseModel):
    page_id: int = Field(..., example=1)
    title: str = Field(..., min_length=1, max_length=255, example="Новость")
    poster: str = Field(..., example="https://example.com/poster.jpg")
    content: str = Field(..., example="Содержание новости")

class PageNewsResponse(BaseModel):
    id: int = Field(..., example=1)
    page_id: int = Field(..., example=1)
    title: str = Field(..., example="Новость")
    poster: str = Field(..., example="https://example.com/poster.jpg")
    content: str = Field(..., example="Содержание новости")

    class Config:
        from_attributes = True

class CreatePageNewsComment(BaseModel):
    page_news_id: int = Field(..., example=1)
    comment: str = Field(..., example="Комментарий к новости")

class PageNewsCommentResponse(BaseModel):
    id: int = Field(..., example=1)
    page_news_id: int = Field(..., example=1)
    user_id: int = Field(..., example=1)
    comment: str = Field(..., example="Комментарий к новости")

    class Config:
        from_attributes = True 