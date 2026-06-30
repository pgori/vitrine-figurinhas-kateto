"""cria modelos de vendedores, leads e round robin

Revision ID: 20260630_0001
Revises:
Create Date: 2026-06-30
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20260630_0001"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "sellers",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("queue_order", sa.Integer(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.CheckConstraint("queue_order > 0", name="ck_sellers_queue_order_positive"),
        sa.UniqueConstraint("name", name="uq_sellers_name"),
        sa.UniqueConstraint("queue_order", name="uq_sellers_queue_order"),
    )

    op.create_table(
        "round_robin_state",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("next_seller_order", sa.Integer(), nullable=False),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.CheckConstraint("id = 1", name="ck_round_robin_state_singleton"),
        sa.CheckConstraint(
            "next_seller_order > 0",
            name="ck_round_robin_state_next_seller_order_positive",
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "leads",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("desired_item", sa.String(length=180), nullable=False),
        sa.Column("phone", sa.String(length=40), nullable=False),
        sa.Column("kanban_column", sa.String(length=60), nullable=False),
        sa.Column("assigned_seller_id", sa.Integer(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["assigned_seller_id"], ["sellers.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_leads_assigned_seller_id", "leads", ["assigned_seller_id"])

    sellers_table = sa.table(
        "sellers",
        sa.column("name", sa.String),
        sa.column("queue_order", sa.Integer),
    )
    op.bulk_insert(
        sellers_table,
        [
            {"name": "Marcelo", "queue_order": 1},
            {"name": "Rafael", "queue_order": 2},
            {"name": "Renato", "queue_order": 3},
            {"name": "Pedro", "queue_order": 4},
            {"name": "Leonardo", "queue_order": 5},
        ],
    )

    state_table = sa.table(
        "round_robin_state",
        sa.column("id", sa.Integer),
        sa.column("next_seller_order", sa.Integer),
    )
    op.bulk_insert(state_table, [{"id": 1, "next_seller_order": 1}])


def downgrade() -> None:
    op.drop_index("ix_leads_assigned_seller_id", table_name="leads")
    op.drop_table("leads")
    op.drop_table("round_robin_state")
    op.drop_table("sellers")
