"""add website account authentication

Revision ID: 008_add_web_account_auth
Revises: 007_add_payment_provider_fields
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = "008_add_web_account_auth"
down_revision = "007_add_payment_provider_fields"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "web_accounts",
        sa.Column("id", sa.BigInteger(), primary_key=True),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("phone", sa.String(length=64), nullable=False),
        sa.Column("phone_normalized", sa.String(length=16), nullable=False),
        sa.Column("password_hash", sa.Text(), nullable=True),
        sa.Column("email_verification_token_hash", sa.String(length=64), nullable=True),
        sa.Column("email_verification_sent_at", sa.DateTime(), nullable=True),
        sa.Column("email_verification_expires_at", sa.DateTime(), nullable=True),
        sa.Column("email_verified_at", sa.DateTime(), nullable=True),
        sa.Column("temporary_password_sent_at", sa.DateTime(), nullable=True),
        sa.Column("password_reset_token_hash", sa.String(length=64), nullable=True),
        sa.Column("password_reset_sent_at", sa.DateTime(), nullable=True),
        sa.Column("password_reset_expires_at", sa.DateTime(), nullable=True),
        sa.Column("must_change_password", sa.Boolean(), server_default=sa.text("false"), nullable=False),
        sa.Column("status", sa.String(length=32), server_default="email_pending", nullable=False),
        sa.Column("trial_used", sa.Boolean(), server_default=sa.text("false"), nullable=False),
        sa.Column("last_login_at", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint("email", name="uq_web_accounts_email"),
        sa.UniqueConstraint("phone_normalized", name="uq_web_accounts_phone_normalized"),
        sa.UniqueConstraint("email_verification_token_hash", name="uq_web_accounts_email_verification_token_hash"),
        sa.UniqueConstraint("password_reset_token_hash", name="uq_web_accounts_password_reset_token_hash"),
    )
    op.create_index("ix_web_accounts_email", "web_accounts", ["email"])
    op.create_index("ix_web_accounts_phone_normalized", "web_accounts", ["phone_normalized"])
    op.create_index("ix_web_accounts_status", "web_accounts", ["status"])

    op.create_table(
        "access_entitlements",
        sa.Column("id", sa.BigInteger(), primary_key=True),
        sa.Column("account_id", sa.BigInteger(), sa.ForeignKey("web_accounts.id"), nullable=False),
        sa.Column("access_status", sa.String(length=32), server_default="email_pending", nullable=False),
        sa.Column("access_type", sa.String(length=32), nullable=True),
        sa.Column("trial_start_at", sa.DateTime(), nullable=True),
        sa.Column("trial_end_at", sa.DateTime(), nullable=True),
        sa.Column("paid_start_at", sa.DateTime(), nullable=True),
        sa.Column("paid_end_at", sa.DateTime(), nullable=True),
        sa.Column("current_period_end", sa.DateTime(), nullable=True),
        sa.Column("revoked_at", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint("account_id", name="uq_access_entitlements_account_id"),
    )
    op.create_index("ix_access_entitlements_account_id", "access_entitlements", ["account_id"])
    op.create_index("ix_access_entitlements_access_status", "access_entitlements", ["access_status"])
    op.create_index("ix_access_entitlements_current_period_end", "access_entitlements", ["current_period_end"])
    op.create_index("ix_access_entitlements_status_end", "access_entitlements", ["access_status", "current_period_end"])

    op.create_table(
        "web_sessions",
        sa.Column("id", sa.BigInteger(), primary_key=True),
        sa.Column("account_id", sa.BigInteger(), sa.ForeignKey("web_accounts.id"), nullable=False),
        sa.Column("session_token_hash", sa.String(length=64), nullable=False),
        sa.Column("expires_at", sa.DateTime(), nullable=False),
        sa.Column("revoked_at", sa.DateTime(), nullable=True),
        sa.Column("last_seen_at", sa.DateTime(), nullable=True),
        sa.Column("user_agent_hash", sa.String(length=64), nullable=True),
        sa.Column("ip_hash", sa.String(length=64), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint("session_token_hash", name="uq_web_sessions_token_hash"),
    )
    op.create_index("ix_web_sessions_account_id", "web_sessions", ["account_id"])
    op.create_index("ix_web_sessions_session_token_hash", "web_sessions", ["session_token_hash"])
    op.create_index("ix_web_sessions_expires_at", "web_sessions", ["expires_at"])
    op.create_index("ix_web_sessions_revoked_at", "web_sessions", ["revoked_at"])

    op.create_table(
        "account_audit_events",
        sa.Column("id", sa.BigInteger(), primary_key=True),
        sa.Column("account_id", sa.BigInteger(), sa.ForeignKey("web_accounts.id"), nullable=True),
        sa.Column("event_type", sa.String(length=64), nullable=False),
        sa.Column("occurred_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column("payload", postgresql.JSONB(), nullable=True),
    )
    op.create_index("ix_account_audit_events_account_id", "account_audit_events", ["account_id"])
    op.create_index("ix_account_audit_events_event_type", "account_audit_events", ["event_type"])
    op.create_index("ix_account_audit_events_occurred_at", "account_audit_events", ["occurred_at"])


def downgrade() -> None:
    op.drop_index("ix_account_audit_events_occurred_at", table_name="account_audit_events")
    op.drop_index("ix_account_audit_events_event_type", table_name="account_audit_events")
    op.drop_index("ix_account_audit_events_account_id", table_name="account_audit_events")
    op.drop_table("account_audit_events")
    op.drop_index("ix_web_sessions_revoked_at", table_name="web_sessions")
    op.drop_index("ix_web_sessions_expires_at", table_name="web_sessions")
    op.drop_index("ix_web_sessions_session_token_hash", table_name="web_sessions")
    op.drop_index("ix_web_sessions_account_id", table_name="web_sessions")
    op.drop_table("web_sessions")
    op.drop_index("ix_access_entitlements_status_end", table_name="access_entitlements")
    op.drop_index("ix_access_entitlements_current_period_end", table_name="access_entitlements")
    op.drop_index("ix_access_entitlements_access_status", table_name="access_entitlements")
    op.drop_index("ix_access_entitlements_account_id", table_name="access_entitlements")
    op.drop_table("access_entitlements")
    op.drop_index("ix_web_accounts_status", table_name="web_accounts")
    op.drop_index("ix_web_accounts_phone_normalized", table_name="web_accounts")
    op.drop_index("ix_web_accounts_email", table_name="web_accounts")
    op.drop_table("web_accounts")
