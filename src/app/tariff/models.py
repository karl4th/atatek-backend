from datetime import datetime

from sqlalchemy import Integer, String, Boolean, DateTime, func
from sqlalchemy.orm import mapped_column, Mapped

from src.app.db.core import Base


class Tariff(Base):
    __tablename__ = "tariffs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    price: Mapped[int] = mapped_column(Integer, nullable=False)

    t_add_child: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    t_edit_child: Mapped[int] = mapped_column(Integer, nullable=False, default=1)

    t_family_count: Mapped[int] = mapped_column(Integer, nullable=False, default=10)

    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), server_onupdate=func.now(), nullable=True)

    
    
class UserTariff(Base):
    __tablename__ = "user_tariffs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    user_id: Mapped[int] = mapped_column(Integer, nullable=False)
    tariff_id: Mapped[int] = mapped_column(Integer, nullable=False)

    t_add_child: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    t_edit_child: Mapped[int] = mapped_column(Integer, nullable=False, default=1)

    t_family_count: Mapped[int] = mapped_column(Integer, nullable=False, default=10)

    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    start_date: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    end_date: Mapped[datetime] = mapped_column(DateTime, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), server_onupdate=func.now(), nullable=True)
