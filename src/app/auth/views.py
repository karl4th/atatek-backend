from fastapi import APIRouter, Response
from fastapi.params import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status
from sqlalchemy import text

from src.app.config.response import *
from src.app.db.core import get_db
from src.app.auth.schemas import *
from src.app.auth.service import UsersService
from src.app.config.auth import auth
from src.app.config.base import settings

router = APIRouter()

@router.post("/login", response_model=StandardResponse[UserResponse])
@autowrap
async def login(user_data: LoginUser, response: Response, db: AsyncSession = Depends(get_db)):
    service = UsersService(db)
    new_user = await service.login_user(user_data)
    access_token, refresh_token, csrf_token = auth.create_tokens(
        new_user['id'],
        additional_data={
            "role": new_user['role'],
            "tariff": new_user['tariff']
        }
    )
    auth.set_tokens_in_cookies(response, access_token, refresh_token, csrf_token)
    return new_user


@router.post("/logout")
async def logout(response: Response):
    access_token = ''
    refresh_token = ''
    csrf_token = ''
    auth.set_tokens_in_cookies(response, access_token, refresh_token, csrf_token)
    return {"message": "Logged out successfully"}

@router.post("/signup", response_model=StandardResponse[UserResponse])
@autowrap
async def signup(user_data: CreateUser, db: AsyncSession = Depends(get_db)):
    service = UsersService(db)
    result = await service.create_new_user(user_data)
    return result

@router.post("/set-address", response_model=StandardResponse[dict])
@autowrap
async def set_address(address: int, user_data = Depends(auth.get_user_data_dependency()), db: AsyncSession = Depends(get_db)):
    service = UsersService(db)
    user = await service.set_address(address, int(user_data["sub"]))
    return user

@router.post("/set-user-page", response_model=StandardResponse[dict])
@autowrap
async def set_user_page(page_id: int, user_data = Depends(auth.get_user_data_dependency()), db: AsyncSession = Depends(get_db)):
    service = UsersService(db)
    user = await service.set_user_page(page_id, int(user_data["sub"]))
    return user


@router.get("/get-me", response_model=StandardResponse[UserResponse])
@autowrap
async def get_me(user_data = Depends(auth.get_user_data_dependency()), db: AsyncSession = Depends(get_db)):
    service = UsersService(db)
    user = await service.get_user_by_id(int(user_data["sub"]))
    return user

@router.get("/get-profile", response_model=StandardResponse[ProfileUser])
@autowrap
async def get_profile(user_data = Depends(auth.get_user_data_dependency()), db: AsyncSession = Depends(get_db)):
    service = UsersService(db)
    user = await service.get_profile(int(user_data["sub"]))
    return user


@router.put("/update-user", response_model=StandardResponse[dict])
@autowrap
async def update_user(user_pass: UpdateUser, user_data = Depends(auth.get_user_data_dependency()), db: AsyncSession = Depends(get_db)):
    service = UsersService(db)
    user = await service.update_user(int(user_data["sub"]), user_pass)
    return user

@router.put("/reset-password", response_model=StandardResponse[dict])
@autowrap   
async def reset_password(user_pass: ResetPassword, user_data = Depends(auth.get_user_data_dependency()), db: AsyncSession = Depends(get_db)):
    service = UsersService(db)
    user = await service.reset_password(int(user_data["sub"]), user_pass)
    return user


@router.get('/my-page', response_model=StandardResponse[dict])
@autowrap
async def my_page(user_data = Depends(auth.get_user_data_dependency()), db: AsyncSession = Depends(get_db)):
    service = UsersService(db)
    user = await service.get_my_page(int(user_data["sub"]))
    return user

@router.post('/test')
async def test():
    return {
        "h": settings.DB_HOST,
        "p": settings.DB_PORT,
        "n": settings.DB_NAME,
        "u": settings.DB_USER,
        "p": settings.DB_PASSWORD
    }