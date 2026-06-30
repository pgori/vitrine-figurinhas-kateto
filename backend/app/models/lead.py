from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Column, DateTime, String
from sqlmodel import Field, Relationship, SQLModel

from app.models.base import utc_now

if TYPE_CHECKING:
    from app.models.seller import Seller

KANBAN_COLUMN_NO_CONTACT = "Sem Contato"


class Lead(SQLModel, table=True):
    __tablename__ = "leads"

    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(sa_column=Column(String(120), nullable=False))
    desired_item: str = Field(sa_column=Column(String(180), nullable=False))
    phone: str = Field(sa_column=Column(String(40), nullable=False))
    kanban_column: str = Field(
        default=KANBAN_COLUMN_NO_CONTACT,
        sa_column=Column(String(60), nullable=False),
    )
    assigned_seller_id: int = Field(foreign_key="sellers.id", nullable=False, index=True)
    created_at: datetime = Field(
        default_factory=utc_now,
        sa_column=Column(DateTime(timezone=True), nullable=False),
    )
    updated_at: datetime = Field(
        default_factory=utc_now,
        sa_column=Column(DateTime(timezone=True), nullable=False),
    )

    assigned_seller: "Seller" = Relationship(back_populates="leads")
