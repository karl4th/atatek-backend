from pydantic import BaseModel, Field
from typing import Optional
from src.app.role.schemas import BaseRole
from src.app.tariff.schemas import BaseTariff

class CreateUser(BaseModel):
    first_name: str = Field(..., min_length=2, max_length=50, example="John")
    last_name: str = Field(..., min_length=2, max_length=50, example="Doe")
    middle_name: Optional[str] = Field(None, min_length=2, max_length=50, example="John")                               
    password: str = Field(..., min_length=8, max_length=100, example="password")
    phone: str = Field(..., example="+77761174378")


class UserResponse(BaseModel):
    id: int = Field(..., example=1)                             
    first_name: str = Field(..., example="John")
    last_name: str = Field(..., example="Doe")
    middle_name: Optional[str] = Field(None, example="John")
    phone: str = Field(..., example="+77761174378")
    role: Optional[BaseRole] = Field(None)
    tariff: Optional[BaseTariff] = Field(None)
    
class BaseUser(BaseModel):
    id: int = Field(..., example=1)                             
    first_name: str = Field(..., example="John")
    last_name: str = Field(..., example="Doe")
    phone: str = Field(..., example="+77761174378")

    class Config:
        from_attributes = True
                                                                                        
    
class LoginUser(BaseModel):
    phone: str = Field(..., example="+77761174378")
    password: str = Field(..., example="password")


class ProfileUser(BaseModel):
    id: int = Field(..., example=1)
    first_name: str = Field(..., example="John")
    last_name: str = Field(..., example="Doe")
    middle_name: Optional[str] = Field(None, example="John")
    phone: str = Field(..., example="+77761174378")
    created_at: str = Field(..., example="2021-01-01")
    address: Optional[str] = Field(None, example="Moscow")
    all_added_nodes: int = Field(..., example=10)
    all_edited_nodes: int = Field(..., example=10)
    all_family_nodes: int = Field(..., example=10)

class UpdateUser(BaseModel):
    first_name: Optional[str] = Field(None, example="John")
    last_name: Optional[str] = Field(None, example="Doe")
    middle_name: Optional[str] = Field(None, example="John")

class ResetPassword(BaseModel):
    password: str = Field(..., example="password")
    new_password: str = Field(..., example="new_password")
    confirm_password: str = Field(..., example="confirm_password")


