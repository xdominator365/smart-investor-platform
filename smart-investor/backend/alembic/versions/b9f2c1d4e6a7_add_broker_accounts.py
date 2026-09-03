"""add broker accounts

Revision ID: b9f2c1d4e6a7
Revises: 229d8f785b73
Create Date: 2026-09-03

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "b9f2c1d4e6a7"
down_revision: Union[str, Sequence[str], None] = "229d8f785b73"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "broker_accounts",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("broker", sa.String(), nullable=False),
        sa.Column("broker_user_id", sa.String(), nullable=False),
        sa.Column("access_token_encrypted", sa.String(), nullable=False),
        sa.Column("connected_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id"),
    )
    op.create_index("ix_broker_accounts_user_id", "broker_accounts", ["user_id"], unique=True)


def downgrade() -> None:
    op.drop_index("ix_broker_accounts_user_id", table_name="broker_accounts")
    op.drop_table("broker_accounts")
