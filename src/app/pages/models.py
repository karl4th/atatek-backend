from datetime import datetime

from sqlalchemy import Integer, String, Boolean, DateTime, func
from sqlalchemy.orm import mapped_column, Mapped

from src.app.db.core import Base


class Page(Base):
    __tablename__ = 'pages'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    title: Mapped[str] = mapped_column(String(255), nullable=False)
    tree_id: Mapped[int] = mapped_column(Integer, nullable=False)

    bread1: Mapped[str] = mapped_column(String(255), nullable=False)
    bread2: Mapped[str] = mapped_column(String(255), nullable=False)
    bread3: Mapped[str] = mapped_column(String(255), nullable=False)

    main_gen: Mapped[int] = mapped_column(Integer, nullable=False)
    main_gen_child: Mapped[int] = mapped_column(Integer, nullable=False)

    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), server_onupdate=func.now(), nullable=True)
    
class UserPage(Base):
    __tablename__ = 'user_page'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    user_id: Mapped[int] = mapped_column(Integer, nullable=False)
    page_id: Mapped[int] = mapped_column(Integer, nullable=False)

    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), server_onupdate=func.now(), nullable=True)            

class PageModerator(Base):
    __tablename__ = 'page_moderator'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    page_id: Mapped[int] = mapped_column(Integer, nullable=False)
    user_id: Mapped[int] = mapped_column(Integer, nullable=False)
    

    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), server_onupdate=func.now(), nullable=True)
