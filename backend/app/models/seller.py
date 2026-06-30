from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, Column, DateTime, String, UniqueConstraint
from sqlmodel import Field, Relationship, SQLModel

from app.models.base import utc_now

if TYPE_CHECKING:
    from app.models.lead import Lead


class Seller(SQLModel, table=True):
    __tablename__ = "sellers"
    __table_args__ = (
        CheckConstraint("queue_order > 0", name="ck_sellers_queue_order_positive"),
        UniqueConstraint("name", name="uq_sellers_name"),
        UniqueConstraint("queue_order", name="uq_sellers_queue_order"),
    )

    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(sa_column=Column(String(120), nullable=False))
    queue_order: int = Field(nullable=False, gt=0)
    created_at: datetime = Field(
        default_factory=utc_now,
        sa_column=Column(DateTime(timezone=True), nullable=False),
    )
    updated_at: datetime = Field(
        default_factory=utc_now,
        sa_column=Column(DateTime(timezone=True), nullable=False),
    )

    leads: list["Lead"] = Relationship(back_populates="assigned_seller")
