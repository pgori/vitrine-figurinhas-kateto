from datetime import datetime

from sqlalchemy import CheckConstraint, Column, DateTime
from sqlmodel import Field, SQLModel

from app.models.base import utc_now


class RoundRobinState(SQLModel, table=True):
    __tablename__ = "round_robin_state"
    __table_args__ = (
        CheckConstraint("id = 1", name="ck_round_robin_state_singleton"),
        CheckConstraint(
            "next_seller_order > 0",
            name="ck_round_robin_state_next_seller_order_positive",
        ),
    )

    id: int = Field(default=1, primary_key=True)
    next_seller_order: int = Field(nullable=False, gt=0)
    updated_at: datetime = Field(
        default_factory=utc_now,
        sa_column=Column(DateTime(timezone=True), nullable=False),
    )
