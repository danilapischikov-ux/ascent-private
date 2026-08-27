"""create reminders

Revision ID: 005_create_reminders
Revises: 004_create_channel_access
"""
from alembic import op
import sqlalchemy as sa

revision = "005_create_reminders"
down_revision = "004_create_channel_access"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "reminders",
        sa.Column("id", sa.BigInteger(), primary_key=True),
        sa.Column("user_id", sa.BigInteger(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("subscription_id", sa.BigInteger(), sa.ForeignKey("subscriptions.id"), nullable=False),
        sa.Column("type", sa.String(length=32), nullable=False),
        sa.Column("send_at", sa.DateTime(), nullable=False),
        sa.Column("sent_at", sa.DateTime(), nullable=True),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_reminders_user_id", "reminders", ["user_id"])
    op.create_index("ix_reminders_subscription_id", "reminders", ["subscription_id"])
    op.create_index("ix_reminders_send_at", "reminders", ["send_at"])


def downgrade() -> None:
    op.drop_index("ix_reminders_send_at", table_name="reminders")
    op.drop_index("ix_reminders_subscription_id", table_name="reminders")
    op.drop_index("ix_reminders_user_id", table_name="reminders")
    op.drop_table("reminders")
