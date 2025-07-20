from datetime import datetime

from sqlalchemy import Integer, String, Boolean, DateTime, func, Text
from sqlalchemy.orm import mapped_column, Mapped

from src.app.db.core import Base


class PagePopularPeoples(Base):
    __tablename__ = 'page_popular_peoples'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    page_id: Mapped[int] = mapped_column(Integer, nullable=False)

    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    date_of_birth: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    death_date: Mapped[datetime] = mapped_column(DateTime, nullable=True)

    bio: Mapped[str] = mapped_column(Text, nullable=True)

    image: Mapped[str] = mapped_column(String(255), nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), server_onupdate=func.now(), nullable=True)
