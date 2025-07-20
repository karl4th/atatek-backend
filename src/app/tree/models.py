from datetime import datetime

from sqlalchemy import Text, func, Integer
from sqlalchemy.orm import Mapped, mapped_column

from src.app.db.core import Base


class Tree(Base):
    __tablename__ = 'tree'

    id: Mapped[int] = mapped_column(primary_key=True)

    name: Mapped[str] = mapped_column(unique=True, nullable=False)
    birth: Mapped[str] = mapped_column(nullable=True)
    death: Mapped[str] = mapped_column(nullable=True)
    bio: Mapped[str] = mapped_column(Text, nullable=True)

    mini_icon: Mapped[str] = mapped_column(nullable=True)
    main_icon: Mapped[str] = mapped_column(nullable=True)

    created_by: Mapped[int] = mapped_column(nullable=True, default=1)
    updated_by: Mapped[int] = mapped_column(nullable=True)

    created_at: Mapped[datetime] = mapped_column(nullable=True, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(nullable=True, server_default=func.now(), server_onupdate=func.now())

    is_deleted: Mapped[bool] = mapped_column(nullable=True, default=False)
    t_id: Mapped[int] = mapped_column(nullable=False)
    parent_id: Mapped[int] = mapped_column(Integer, nullable=True)
