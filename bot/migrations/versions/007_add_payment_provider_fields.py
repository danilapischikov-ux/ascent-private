"""add payment provider fields

Revision ID: 007_add_payment_provider_fields
Revises: 006_create_marketing_analytics
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = "007_add_payment_provider_fields"
down_revision = "006_create_marketing_analytics"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("payments", sa.Column("provider", sa.String(length=32), nullable=True))
    op.add_column("payments", sa.Column("provider_payment_id", sa.String(length=128), nullable=True))
    op.add_column("payments", sa.Column("provider_status", sa.String(length=64), nullable=True))
    op.add_column("payments", sa.Column("provider_confirmation_url", sa.Text(), nullable=True))
    op.add_column("payments", sa.Column("provider_created_payload", postgresql.JSONB(), nullable=True))
    op.add_column("payments", sa.Column("provider_webhook_payload", postgresql.JSONB(), nullable=True))
    op.create_unique_constraint(
        "uq_payments_provider_payment_id",
        "payments",
        ["provider_payment_id"],
    )
    op.create_index("ix_payments_provider", "payments", ["provider"])


def downgrade() -> None:
    op.drop_index("ix_payments_provider", table_name="payments")
    op.drop_constraint("uq_payments_provider_payment_id", "payments", type_="unique")
    op.drop_column("payments", "provider_webhook_payload")
    op.drop_column("payments", "provider_created_payload")
    op.drop_column("payments", "provider_confirmation_url")
    op.drop_column("payments", "provider_status")
    op.drop_column("payments", "provider_payment_id")
    op.drop_column("payments", "provider")
