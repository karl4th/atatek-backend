from datetime import datetime

from sqlalchemy import Integer, String, Boolean, DateTime, func, Enum as SQLEnum
from sqlalchemy.orm import mapped_column, Mapped

from src.app.db.core import Base
from enum import Enum

class TicketType(Enum):
    add_data = "add_data"
    edit_data = "edit_data"

class TicketStatus(Enum):
    pending = "pending"
    approved = "approved"
    rejected = "rejected"

class Ticket(Base):
    __tablename__ = "tickets"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    ticket_type: Mapped[str] = mapped_column(SQLEnum(TicketType), nullable=False)
    status: Mapped[str] = mapped_column(SQLEnum(TicketStatus), nullable=False)

    created_by: Mapped[int] = mapped_column(Integer, nullable=False)
    answered_by: Mapped[int] = mapped_column(Integer, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), server_onupdate=func.now(), nullable=True)


class TicketAddData(Base):
    __tablename__ = "ticket_add_data"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    ticket_id: Mapped[int] = mapped_column(Integer, nullable=False)

    parent_id: Mapped[int] = mapped_column(Integer, nullable=False)

    name: Mapped[str] = mapped_column(String(255), nullable=False)

    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), server_onupdate=func.now(), nullable=True)

class TicketEditData(Base):
    __tablename__ = "ticket_edit_data"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    ticket_id: Mapped[int] = mapped_column(Integer, nullable=False)

    tree_id: Mapped[int] = mapped_column(Integer, nullable=False)

    new_name: Mapped[str] = mapped_column(String(255), nullable=False)
    new_bio: Mapped[str] = mapped_column(String(255), nullable=True)
    new_birth: Mapped[str] = mapped_column(String(255), nullable=True)
    new_death: Mapped[str] = mapped_column(String(255), nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), server_onupdate=func.now(), nullable=True)

