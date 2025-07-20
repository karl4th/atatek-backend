from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from src.app.config.response import StandardResponse, autowrap
from src.app.db.core import get_db
from src.app.page_news.schemas import *
from src.app.page_news.service import PageNewsService
from src.app.config.auth import auth

router = APIRouter()

@router.post("/create", response_model=StandardResponse[PageNewsResponse])
@autowrap
async def create_news(
    news_data: CreatePageNews,
    user_data = Depends(auth.get_user_data_dependency()),
    db: AsyncSession = Depends(get_db)
):
    service = PageNewsService(db)
    news = await service.create_news(news_data)
    return news

@router.get("/{news_id}", response_model=StandardResponse[PageNewsResponse])
@autowrap
async def get_news(
    news_id: int,
    db: AsyncSession = Depends(get_db)
):
    service = PageNewsService(db)
    news = await service.get_news_by_id(news_id)
    return news

@router.get("/page/{page_id}", response_model=StandardResponse[list[PageNewsResponse]])
@autowrap
async def get_news_by_page(
    page_id: int,
    db: AsyncSession = Depends(get_db)
):
    service = PageNewsService(db)
    news = await service.get_news_by_page_id(page_id)
    return news

@router.put("/{news_id}", response_model=StandardResponse[PageNewsResponse])
@autowrap
async def update_news(
    news_id: int,
    news_data: CreatePageNews,
    user_data = Depends(auth.get_user_data_dependency()),
    db: AsyncSession = Depends(get_db)
):
    service = PageNewsService(db)
    news = await service.update_news(news_id, news_data)
    return news

@router.delete("/{news_id}", response_model=StandardResponse[bool])
@autowrap
async def delete_news(
    news_id: int,
    user_data = Depends(auth.get_user_data_dependency()),
    db: AsyncSession = Depends(get_db)
):
    service = PageNewsService(db)
    result = await service.delete_news(news_id)
    return result

@router.post("/comment", response_model=StandardResponse[PageNewsCommentResponse])
@autowrap
async def create_comment(
    comment_data: CreatePageNewsComment,
    user_data = Depends(auth.get_user_data_dependency()),
    db: AsyncSession = Depends(get_db)
):
    service = PageNewsService(db)
    comment = await service.create_comment(comment_data, int(user_data["sub"]))
    return comment

@router.get("/{news_id}/comments", response_model=StandardResponse[list[PageNewsCommentResponse]])
@autowrap
async def get_comments(
    news_id: int,
    db: AsyncSession = Depends(get_db)
):
    service = PageNewsService(db)
    comments = await service.get_comments_by_news_id(news_id)
    return comments

@router.delete("/comment/{comment_id}", response_model=StandardResponse[bool])
@autowrap
async def delete_comment(
    comment_id: int,
    user_data = Depends(auth.get_user_data_dependency()),
    db: AsyncSession = Depends(get_db)
):
    service = PageNewsService(db)
    result = await service.delete_comment(comment_id)
    return result 