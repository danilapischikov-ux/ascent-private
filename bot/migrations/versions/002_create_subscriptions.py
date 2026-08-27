"""create subscriptions

Revision ID: 002_create_subscriptions
Revises: 001_create_users
"""
from alembic import op
import sqlalchemy as sa

revision = "002_create_subscriptions"
down_revision = "001_create_users"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "subscriptions",
        sa.Column("id", sa.BigInteger(), primary_key=True),
        sa.Column("user_id", sa.BigInteger(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("type", sa.String(length=32), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("start_date", sa.DateTime(), nullable=False),
        sa.Column("end_date", sa.DateTime(), nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_subscriptions_user_id", "subscriptions", ["user_id"])
    op.create_index("ix_subscriptions_status", "subscriptions", ["status"])
    op.create_index("ix_subscriptions_end_date", "subscriptions", ["end_date"])
    op.create_index(
        "ix_subscriptions_user_status_end",
        "subscriptions",
        ["user_id", "status", "end_date"],
    )


def downgrade() -> None:
    op.drop_index("ix_subscriptions_user_status_end", table_name="subscriptions")
    op.drop_index("ix_subscriptions_end_date", table_name="subscriptions")
    op.drop_index("ix_subscriptions_status", table_name="subscriptions")
    op.drop_index("ix_subscriptions_user_id", table_name="subscriptions")
    op.drop_table("subscriptions")
