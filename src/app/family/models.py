from datetime import datetime

from sqlalchemy import Text, func, Integer, String, ARRAY
from sqlalchemy.orm import Mapped, mapped_column

from src.app.db.core import Base

class Family(Base):
    __tablename__ = 'family'

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, nullable=False)

    full_name: Mapped[str] = mapped_column(nullable=False)
    date_of_birth: Mapped[str] = mapped_column(nullable=False)

    is_alive: Mapped[bool] = mapped_column(nullable=False, default=True)
    death_date: Mapped[str] = mapped_column(nullable=True)

    bio: Mapped[str] = mapped_column(Text, nullable=True)
    sex: Mapped[str] = mapped_column(String, nullable=False)
    img: Mapped[str] = mapped_column(String, nullable=True)

    father_id: Mapped[int] = mapped_column(Integer, nullable=True)
    mother_id: Mapped[int] = mapped_column(Integer, nullable=True)
    partners_id: Mapped[list[int]] = mapped_column(ARRAY(Integer), nullable=True)
    
    created_at: Mapped[datetime] = mapped_column(nullable=True, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(nullable=True, server_default=func.now(), server_onupdate=func.now())

    is_deleted: Mapped[bool] = mapped_column(nullable=True, default=False)
    
    
 
