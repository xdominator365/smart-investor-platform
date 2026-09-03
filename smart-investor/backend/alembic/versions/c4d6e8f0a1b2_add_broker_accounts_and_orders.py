"""add broker accounts and broker orders

Revision ID: c4d6e8f0a1b2
Revises: b9f2c1d4e6a7
Create Date: 2026-09-03

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "c4d6e8f0a1b2"
down_revision: Union[str, Sequence[str], None] = "b9f2c1d4e6a7"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "broker_orders",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("broker", sa.String(), nullable=False),
        sa.Column("idempotency_key", sa.String(), nullable=False),
        sa.Column("preview_id", sa.String(), nullable=False),
        sa.Column("symbol", sa.String(), nullable=False),
        sa.Column("exchange", sa.String(), nullable=False),
        sa.Column("side", sa.String(), nullable=False),
        sa.Column("quantity", sa.Integer(), nullable=False),
        sa.Column("order_type", sa.String(), nullable=False),
        sa.Column("product", sa.String(), nullable=False),
        sa.Column("reference_price", sa.Float(), nullable=False),
        sa.Column("estimated_value", sa.Float(), nullable=False),
        sa.Column("zerodha_order_id", sa.String(), nullable=True),
        sa.Column("status", sa.String(), nullable=False),
        sa.Column("rejection_reason", sa.String(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("idempotency_key"),
    )
    op.create_index("ix_broker_orders_user_id", "broker_orders", ["user_id"], unique=False)
    op.create_index("ix_broker_orders_idempotency_key", "broker_orders", ["idempotency_key"], unique=True)


def downgrade() -> None:
    op.drop_index("ix_broker_orders_idempotency_key", table_name="broker_orders")
    op.drop_index("ix_broker_orders_user_id", table_name="broker_orders")
    op.drop_table("broker_orders")
