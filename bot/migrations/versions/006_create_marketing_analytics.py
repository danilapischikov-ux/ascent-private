"""create marketing analytics

Revision ID: 006_create_marketing_analytics
Revises: 005_create_reminders
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "006_create_marketing_analytics"
down_revision = "005_create_reminders"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("payments", sa.Column("lead_id", sa.String(length=128), nullable=True))
    op.add_column("payments", sa.Column("session_id", sa.String(length=128), nullable=True))
    op.add_column("payments", sa.Column("client_id", sa.String(length=128), nullable=True))
    op.add_column("payments", sa.Column("yclid", sa.String(length=128), nullable=True))
    op.add_column("payments", sa.Column("attribution", postgresql.JSONB(), nullable=True))
    op.create_index("ix_payments_client_yclid", "payments", ["client_id", "yclid"])

    op.create_table(
        "site_events",
        sa.Column("id", sa.BigInteger(), primary_key=True),
        sa.Column("event_id", sa.String(length=128), nullable=True, unique=True),
        sa.Column("event_type", sa.String(length=64), nullable=False),
        sa.Column("occurred_at", sa.DateTime(), nullable=False),
        sa.Column("received_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column("lead_id", sa.String(length=128), nullable=True),
        sa.Column("session_id", sa.String(length=128), nullable=True),
        sa.Column("client_id", sa.String(length=128), nullable=True),
        sa.Column("yclid", sa.String(length=128), nullable=True),
        sa.Column("payment_token", sa.String(length=128), nullable=True),
        sa.Column("payment_id", sa.BigInteger(), sa.ForeignKey("payments.id"), nullable=True),
        sa.Column("telegram_user_id", sa.BigInteger(), nullable=True),
        sa.Column("url", sa.Text(), nullable=True),
        sa.Column("referrer", sa.Text(), nullable=True),
        sa.Column("user_agent", sa.Text(), nullable=True),
        sa.Column("ip_address", sa.String(length=45), nullable=True),
        sa.Column("attribution", postgresql.JSONB(), nullable=True),
        sa.Column("payload", postgresql.JSONB(), nullable=True),
    )
    op.create_index("ix_site_events_event_type", "site_events", ["event_type"])
    op.create_index("ix_site_events_received_at", "site_events", ["received_at"])
    op.create_index("ix_site_events_lead_id", "site_events", ["lead_id"])
    op.create_index("ix_site_events_session_id", "site_events", ["session_id"])
    op.create_index("ix_site_events_client_id", "site_events", ["client_id"])
    op.create_index("ix_site_events_yclid", "site_events", ["yclid"])
    op.create_index("ix_site_events_payment_token", "site_events", ["payment_token"])
    op.create_index("ix_site_events_payment_id", "site_events", ["payment_id"])
    op.create_index("ix_site_events_telegram_user_id", "site_events", ["telegram_user_id"])
    op.create_index("ix_site_events_type_occurred", "site_events", ["event_type", "occurred_at"])

    op.create_table(
        "lead_attribution",
        sa.Column("id", sa.BigInteger(), primary_key=True),
        sa.Column("lead_id", sa.String(length=128), nullable=True, unique=True),
        sa.Column("session_id", sa.String(length=128), nullable=True),
        sa.Column("client_id", sa.String(length=128), nullable=True),
        sa.Column("yclid", sa.String(length=128), nullable=True),
        sa.Column("payment_token", sa.String(length=128), nullable=True, unique=True),
        sa.Column("payment_id", sa.BigInteger(), sa.ForeignKey("payments.id"), nullable=True, unique=True),
        sa.Column("telegram_user_id", sa.BigInteger(), nullable=True),
        sa.Column("utm_source", sa.String(length=128), nullable=True),
        sa.Column("utm_medium", sa.String(length=128), nullable=True),
        sa.Column("utm_campaign", sa.String(length=255), nullable=True),
        sa.Column("utm_content", sa.String(length=255), nullable=True),
        sa.Column("utm_term", sa.String(length=255), nullable=True),
        sa.Column("first_url", sa.Text(), nullable=True),
        sa.Column("landing_url", sa.Text(), nullable=True),
        sa.Column("referrer", sa.Text(), nullable=True),
        sa.Column("first_seen_at", sa.DateTime(), nullable=True),
        sa.Column("last_seen_at", sa.DateTime(), nullable=True),
        sa.Column("source_payload", postgresql.JSONB(), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_lead_attribution_session_id", "lead_attribution", ["session_id"])
    op.create_index("ix_lead_attribution_client_id", "lead_attribution", ["client_id"])
    op.create_index("ix_lead_attribution_yclid", "lead_attribution", ["yclid"])
    op.create_index("ix_lead_attribution_telegram_user_id", "lead_attribution", ["telegram_user_id"])
    op.create_index("ix_lead_attribution_utm_source", "lead_attribution", ["utm_source"])
    op.create_index("ix_lead_attribution_client_yclid", "lead_attribution", ["client_id", "yclid"])

    op.create_table(
        "raw_direct_reports",
        sa.Column("id", sa.BigInteger(), primary_key=True),
        sa.Column("report_date", sa.Date(), nullable=False),
        sa.Column("report_type", sa.String(length=64), nullable=False),
        sa.Column("campaign_id", sa.String(length=128), nullable=True),
        sa.Column("ad_group_id", sa.String(length=128), nullable=True),
        sa.Column("ad_id", sa.String(length=128), nullable=True),
        sa.Column("keyword_id", sa.String(length=128), nullable=True),
        sa.Column("row_data", postgresql.JSONB(), nullable=False),
        sa.Column("imported_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_raw_direct_reports_report_date", "raw_direct_reports", ["report_date"])
    op.create_index("ix_raw_direct_reports_campaign_id", "raw_direct_reports", ["campaign_id"])
    op.create_index("ix_raw_direct_reports_ad_group_id", "raw_direct_reports", ["ad_group_id"])
    op.create_index("ix_raw_direct_reports_ad_id", "raw_direct_reports", ["ad_id"])
    op.create_index("ix_raw_direct_reports_keyword_id", "raw_direct_reports", ["keyword_id"])
    op.create_index("ix_raw_direct_reports_type_date", "raw_direct_reports", ["report_type", "report_date"])

    op.create_table(
        "raw_metrica_logs",
        sa.Column("id", sa.BigInteger(), primary_key=True),
        sa.Column("log_date", sa.Date(), nullable=False),
        sa.Column("source", sa.String(length=64), nullable=False),
        sa.Column("client_id", sa.String(length=128), nullable=True),
        sa.Column("yclid", sa.String(length=128), nullable=True),
        sa.Column("visit_id", sa.String(length=128), nullable=True),
        sa.Column("hit_id", sa.String(length=128), nullable=True),
        sa.Column("row_data", postgresql.JSONB(), nullable=False),
        sa.Column("imported_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_raw_metrica_logs_log_date", "raw_metrica_logs", ["log_date"])
    op.create_index("ix_raw_metrica_logs_client_id", "raw_metrica_logs", ["client_id"])
    op.create_index("ix_raw_metrica_logs_yclid", "raw_metrica_logs", ["yclid"])
    op.create_index("ix_raw_metrica_logs_visit_id", "raw_metrica_logs", ["visit_id"])
    op.create_index("ix_raw_metrica_logs_hit_id", "raw_metrica_logs", ["hit_id"])
    op.create_index("ix_raw_metrica_logs_source_date", "raw_metrica_logs", ["source", "log_date"])

    op.create_table(
        "analytics_mart_snapshots",
        sa.Column("id", sa.BigInteger(), primary_key=True),
        sa.Column("snapshot_date", sa.Date(), nullable=False),
        sa.Column("window_start", sa.DateTime(), nullable=False),
        sa.Column("window_end", sa.DateTime(), nullable=False),
        sa.Column("segment_id", sa.String(length=128), nullable=False),
        sa.Column("metrics", postgresql.JSONB(), nullable=False),
        sa.Column("source_refs", postgresql.JSONB(), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_analytics_mart_snapshots_snapshot_date", "analytics_mart_snapshots", ["snapshot_date"])
    op.create_index("ix_analytics_mart_snapshots_segment_id", "analytics_mart_snapshots", ["segment_id"])
    op.create_index(
        "ix_analytics_mart_segment_window",
        "analytics_mart_snapshots",
        ["segment_id", "window_start", "window_end"],
    )

    op.create_table(
        "codex_decisions",
        sa.Column("id", sa.BigInteger(), primary_key=True),
        sa.Column("decision_id", sa.String(length=128), nullable=False, unique=True),
        sa.Column("segment_id", sa.String(length=128), nullable=True),
        sa.Column("data_window", postgresql.JSONB(), nullable=True),
        sa.Column("sample_size", sa.Integer(), nullable=True),
        sa.Column("reason_codes", postgresql.JSONB(), nullable=False),
        sa.Column("proposed_action", sa.String(length=64), nullable=True),
        sa.Column("change_value", postgresql.JSONB(), nullable=True),
        sa.Column("confidence", sa.Numeric(5, 4), nullable=True),
        sa.Column("rollback_plan", postgresql.JSONB(), nullable=True),
        sa.Column("compliance_flag", sa.Boolean(), server_default="false", nullable=False),
        sa.Column("status", sa.String(length=32), server_default="pending", nullable=False),
        sa.Column("validation_errors", postgresql.JSONB(), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_codex_decisions_segment_id", "codex_decisions", ["segment_id"])
    op.create_index("ix_codex_decisions_proposed_action", "codex_decisions", ["proposed_action"])
    op.create_index("ix_codex_decisions_status", "codex_decisions", ["status"])

    op.create_table(
        "campaign_snapshots",
        sa.Column("id", sa.BigInteger(), primary_key=True),
        sa.Column("snapshot_at", sa.DateTime(), nullable=False),
        sa.Column("provider", sa.String(length=64), server_default="yandex_direct", nullable=False),
        sa.Column("campaign_id", sa.String(length=128), nullable=True),
        sa.Column("ad_group_id", sa.String(length=128), nullable=True),
        sa.Column("ad_id", sa.String(length=128), nullable=True),
        sa.Column("keyword_id", sa.String(length=128), nullable=True),
        sa.Column("state", postgresql.JSONB(), nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_campaign_snapshots_snapshot_at", "campaign_snapshots", ["snapshot_at"])
    op.create_index("ix_campaign_snapshots_campaign_id", "campaign_snapshots", ["campaign_id"])
    op.create_index("ix_campaign_snapshots_ad_group_id", "campaign_snapshots", ["ad_group_id"])
    op.create_index("ix_campaign_snapshots_ad_id", "campaign_snapshots", ["ad_id"])
    op.create_index("ix_campaign_snapshots_keyword_id", "campaign_snapshots", ["keyword_id"])
    op.create_index("ix_campaign_snapshots_campaign_time", "campaign_snapshots", ["campaign_id", "snapshot_at"])

    op.create_table(
        "action_log",
        sa.Column("id", sa.BigInteger(), primary_key=True),
        sa.Column("action_id", sa.String(length=128), nullable=False, unique=True),
        sa.Column("decision_id", sa.String(length=128), sa.ForeignKey("codex_decisions.decision_id"), nullable=True),
        sa.Column("proposed_action", sa.String(length=64), nullable=False),
        sa.Column("target_type", sa.String(length=64), nullable=True),
        sa.Column("target_id", sa.String(length=128), nullable=True),
        sa.Column("dry_run", sa.Boolean(), server_default="true", nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("previous_state", postgresql.JSONB(), nullable=True),
        sa.Column("new_state", postgresql.JSONB(), nullable=True),
        sa.Column("rollback_payload", postgresql.JSONB(), nullable=True),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("executed_at", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_action_log_proposed_action", "action_log", ["proposed_action"])
    op.create_index("ix_action_log_target_id", "action_log", ["target_id"])
    op.create_index("ix_action_log_status", "action_log", ["status"])

    op.create_table(
        "alerts",
        sa.Column("id", sa.BigInteger(), primary_key=True),
        sa.Column("alert_key", sa.String(length=160), nullable=False, unique=True),
        sa.Column("severity", sa.String(length=16), nullable=False),
        sa.Column("alert_type", sa.String(length=64), nullable=False),
        sa.Column("status", sa.String(length=32), server_default="open", nullable=False),
        sa.Column("payload", postgresql.JSONB(), nullable=False),
        sa.Column("resolved_at", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_alerts_severity", "alerts", ["severity"])
    op.create_index("ix_alerts_alert_type", "alerts", ["alert_type"])
    op.create_index("ix_alerts_status", "alerts", ["status"])


def downgrade() -> None:
    op.drop_index("ix_alerts_status", table_name="alerts")
    op.drop_index("ix_alerts_alert_type", table_name="alerts")
    op.drop_index("ix_alerts_severity", table_name="alerts")
    op.drop_table("alerts")
    op.drop_index("ix_action_log_status", table_name="action_log")
    op.drop_index("ix_action_log_target_id", table_name="action_log")
    op.drop_index("ix_action_log_proposed_action", table_name="action_log")
    op.drop_table("action_log")
    op.drop_index("ix_campaign_snapshots_campaign_time", table_name="campaign_snapshots")
    op.drop_index("ix_campaign_snapshots_keyword_id", table_name="campaign_snapshots")
    op.drop_index("ix_campaign_snapshots_ad_id", table_name="campaign_snapshots")
    op.drop_index("ix_campaign_snapshots_ad_group_id", table_name="campaign_snapshots")
    op.drop_index("ix_campaign_snapshots_campaign_id", table_name="campaign_snapshots")
    op.drop_index("ix_campaign_snapshots_snapshot_at", table_name="campaign_snapshots")
    op.drop_table("campaign_snapshots")
    op.drop_index("ix_codex_decisions_status", table_name="codex_decisions")
    op.drop_index("ix_codex_decisions_proposed_action", table_name="codex_decisions")
    op.drop_index("ix_codex_decisions_segment_id", table_name="codex_decisions")
    op.drop_table("codex_decisions")
    op.drop_index("ix_analytics_mart_segment_window", table_name="analytics_mart_snapshots")
    op.drop_index("ix_analytics_mart_snapshots_segment_id", table_name="analytics_mart_snapshots")
    op.drop_index("ix_analytics_mart_snapshots_snapshot_date", table_name="analytics_mart_snapshots")
    op.drop_table("analytics_mart_snapshots")
    op.drop_index("ix_raw_metrica_logs_source_date", table_name="raw_metrica_logs")
    op.drop_index("ix_raw_metrica_logs_hit_id", table_name="raw_metrica_logs")
    op.drop_index("ix_raw_metrica_logs_visit_id", table_name="raw_metrica_logs")
    op.drop_index("ix_raw_metrica_logs_yclid", table_name="raw_metrica_logs")
    op.drop_index("ix_raw_metrica_logs_client_id", table_name="raw_metrica_logs")
    op.drop_index("ix_raw_metrica_logs_log_date", table_name="raw_metrica_logs")
    op.drop_table("raw_metrica_logs")
    op.drop_index("ix_raw_direct_reports_type_date", table_name="raw_direct_reports")
    op.drop_index("ix_raw_direct_reports_keyword_id", table_name="raw_direct_reports")
    op.drop_index("ix_raw_direct_reports_ad_id", table_name="raw_direct_reports")
    op.drop_index("ix_raw_direct_reports_ad_group_id", table_name="raw_direct_reports")
    op.drop_index("ix_raw_direct_reports_campaign_id", table_name="raw_direct_reports")
    op.drop_index("ix_raw_direct_reports_report_date", table_name="raw_direct_reports")
    op.drop_table("raw_direct_reports")
    op.drop_index("ix_lead_attribution_client_yclid", table_name="lead_attribution")
    op.drop_index("ix_lead_attribution_utm_source", table_name="lead_attribution")
    op.drop_index("ix_lead_attribution_telegram_user_id", table_name="lead_attribution")
    op.drop_index("ix_lead_attribution_yclid", table_name="lead_attribution")
    op.drop_index("ix_lead_attribution_client_id", table_name="lead_attribution")
    op.drop_index("ix_lead_attribution_session_id", table_name="lead_attribution")
    op.drop_table("lead_attribution")
    op.drop_index("ix_site_events_type_occurred", table_name="site_events")
    op.drop_index("ix_site_events_telegram_user_id", table_name="site_events")
    op.drop_index("ix_site_events_payment_id", table_name="site_events")
    op.drop_index("ix_site_events_payment_token", table_name="site_events")
    op.drop_index("ix_site_events_yclid", table_name="site_events")
    op.drop_index("ix_site_events_client_id", table_name="site_events")
    op.drop_index("ix_site_events_session_id", table_name="site_events")
    op.drop_index("ix_site_events_lead_id", table_name="site_events")
    op.drop_index("ix_site_events_received_at", table_name="site_events")
    op.drop_index("ix_site_events_event_type", table_name="site_events")
    op.drop_table("site_events")
    op.drop_index("ix_payments_client_yclid", table_name="payments")
    op.drop_column("payments", "attribution")
    op.drop_column("payments", "yclid")
    op.drop_column("payments", "client_id")
    op.drop_column("payments", "session_id")
    op.drop_column("payments", "lead_id")
