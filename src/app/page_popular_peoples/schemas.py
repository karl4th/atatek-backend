from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class CreatePagePopularPeople(BaseModel):
    page_id: int = Field(..., example=1)
    full_name: str = Field(..., min_length=1, max_length=255, example="Иван Иванов")
    date_of_birth: str = Field(..., example="1990-01-01T00:00:00")
    death_date: Optional[str] = Field(None, example="2020-01-01T00:00:00")
    bio: Optional[str] = Field(None, example="Биография человека")
    image: Optional[str] = Field(None, example="https://example.com/image.jpg")

class PagePopularPeopleResponse(BaseModel):
    id: int = Field(..., example=1)
    page_id: int = Field(..., example=1)
    full_name: str = Field(..., example="Иван Иванов")
    date_of_birth: str = Field(..., example="1990-01-01T00:00:00")
    death_date: Optional[str] = Field(None, example="2020-01-01T00:00:00")
    bio: Optional[str] = Field(None, example="Биография человека")
    image: Optional[str] = Field(None, example="https://example.com/image.jpg")

    class Config:
        from_attributes = True 