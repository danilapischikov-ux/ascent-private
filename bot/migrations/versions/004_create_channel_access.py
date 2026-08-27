"""create channel access

Revision ID: 004_create_channel_access
Revises: 003_create_payments
"""
from alembic import op
import sqlalchemy as sa

revision = "004_create_channel_access"
down_revision = "003_create_payments"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "channel_access",
        sa.Column("id", sa.BigInteger(), primary_key=True),
        sa.Column("user_id", sa.BigInteger(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("subscription_id", sa.BigInteger(), sa.ForeignKey("subscriptions.id"), nullable=False),
        sa.Column("invite_link", sa.Text(), nullable=True),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("expires_at", sa.DateTime(), nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_channel_access_user_id", "channel_access", ["user_id"])
    op.create_index("ix_channel_access_subscription_id", "channel_access", ["subscription_id"])
    op.create_index("ix_channel_access_status", "channel_access", ["status"])
    op.create_index("ix_channel_access_expires_at", "channel_access", ["expires_at"])


def downgrade() -> None:
    op.drop_index("ix_channel_access_expires_at", table_name="channel_access")
    op.drop_index("ix_channel_access_status", table_name="channel_access")
    op.drop_index("ix_channel_access_subscription_id", table_name="channel_access")
    op.drop_index("ix_channel_access_user_id", table_name="channel_access")
    op.drop_table("channel_access")
