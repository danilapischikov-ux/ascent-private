"""create payments

Revision ID: 003_create_payments
Revises: 002_create_subscriptions
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "003_create_payments"
down_revision = "002_create_subscriptions"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "payments",
        sa.Column("id", sa.BigInteger(), primary_key=True),
        sa.Column("user_id", sa.BigInteger(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("telegram_user_id", sa.BigInteger(), nullable=False),
        sa.Column("inv_id", sa.BigInteger(), nullable=True),
        sa.Column("payment_token", sa.String(length=128), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("amount", sa.Numeric(12, 2), nullable=False),
        sa.Column("currency", sa.String(length=8), nullable=False),
        sa.Column("customer_name", sa.String(length=255), nullable=True),
        sa.Column("customer_email", sa.String(length=255), nullable=True),
        sa.Column("customer_phone", sa.String(length=64), nullable=True),
        sa.Column("robokassa_signature", sa.String(length=255), nullable=True),
        sa.Column("paid_at", sa.DateTime(), nullable=True),
        sa.Column("activated_at", sa.DateTime(), nullable=True),
        sa.Column("report_sent_at", sa.DateTime(), nullable=True),
        sa.Column("raw_result", postgresql.JSONB(), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint("inv_id"),
        sa.UniqueConstraint("payment_token"),
    )
    op.create_index("ix_payments_user_id", "payments", ["user_id"])
    op.create_index("ix_payments_telegram_user_id", "payments", ["telegram_user_id"])
    op.create_index("ix_payments_payment_token", "payments", ["payment_token"])
    op.create_index("ix_payments_status", "payments", ["status"])
    op.create_index("ix_payments_pending_token", "payments", ["payment_token", "status"])


def downgrade() -> None:
    op.drop_index("ix_payments_pending_token", table_name="payments")
    op.drop_index("ix_payments_status", table_name="payments")
    op.drop_index("ix_payments_payment_token", table_name="payments")
    op.drop_index("ix_payments_telegram_user_id", table_name="payments")
    op.drop_index("ix_payments_user_id", table_name="payments")
    op.drop_table("payments")
