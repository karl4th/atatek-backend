from fastapi import APIRouter, Response
from fastapi.params import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status
from sqlalchemy import text

from src.app.config.response import *
from src.app.db.core import get_db

router = APIRouter()

@router.get("/health-base", response_model=StandardResponse[dict])
@autowrap
async def health_check(db: AsyncSession = Depends(get_db)):
    try:
        # Пробуем выполнить простой запрос к базе
        await db.execute(text("SELECT 1"))
        return {"status": "healthy", "message": "Database connection is working"}
    except Exception as e:
        return {"status": "unhealthy", "message": f"Database connection failed: {str(e)}"}