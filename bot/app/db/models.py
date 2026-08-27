from datetime import datetime
from datetime import date
from decimal import Decimal

from sqlalchemy import BigInteger, Boolean, Date, DateTime, ForeignKey, Index, Integer, Numeric, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy.sql import func


class Base(DeclarativeBase):
    pass


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )


class User(Base, TimestampMixin):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    telegram_user_id: Mapped[int] = mapped_column(BigInteger, unique=True, nullable=False, index=True)
    username: Mapped[str | None] = mapped_column(String(255))
    first_name: Mapped[str | None] = mapped_column(String(255))
    last_name: Mapped[str | None] = mapped_column(String(255))
    source: Mapped[str | None] = mapped_column(String(64))
    trial_used: Mapped[bool] = mapped_column(Boolean, default=False, server_default="false", nullable=False)

    subscriptions: Mapped[list["Subscription"]] = relationship(back_populates="user")
    payments: Mapped[list["Payment"]] = relationship(back_populates="user")


class Subscription(Base, TimestampMixin):
    __tablename__ = "subscriptions"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    type: Mapped[str] = mapped_column(String(32), nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False, index=True)
    start_date: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    end_date: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)

    user: Mapped[User] = relationship(back_populates="subscriptions")


class Payment(Base, TimestampMixin):
    __tablename__ = "payments"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    telegram_user_id: Mapped[int] = mapped_column(BigInteger, nullable=False, index=True)
    inv_id: Mapped[int | None] = mapped_column(BigInteger, unique=True)
    payment_token: Mapped[str] = mapped_column(String(128), unique=True, nullable=False, index=True)
    status: Mapped[str] = mapped_column(String(32), nullable=False, index=True, default="pending")
    amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    currency: Mapped[str] = mapped_column(String(8), nullable=False)
    customer_name: Mapped[str | None] = mapped_column(String(255))
    customer_email: Mapped[str | None] = mapped_column(String(255))
    customer_phone: Mapped[str | None] = mapped_column(String(64))
    lead_id: Mapped[str | None] = mapped_column(String(128))
    session_id: Mapped[str | None] = mapped_column(String(128))
    client_id: Mapped[str | None] = mapped_column(String(128))
    yclid: Mapped[str | None] = mapped_column(String(128))
    attribution: Mapped[dict | None] = mapped_column(JSONB)
    robokassa_signature: Mapped[str | None] = mapped_column(String(255))
    provider: Mapped[str | None] = mapped_column(String(32))
    provider_payment_id: Mapped[str | None] = mapped_column(String(128), unique=True)
    provider_status: Mapped[str | None] = mapped_column(String(64))
    provider_confirmation_url: Mapped[str | None] = mapped_column(Text)
    provider_created_payload: Mapped[dict | None] = mapped_column(JSONB)
    provider_webhook_payload: Mapped[dict | None] = mapped_column(JSONB)
    paid_at: Mapped[datetime | None] = mapped_column(DateTime)
    activated_at: Mapped[datetime | None] = mapped_column(DateTime)
    report_sent_at: Mapped[datetime | None] = mapped_column(DateTime)
    raw_result: Mapped[dict | None] = mapped_column(JSONB)

    user: Mapped[User] = relationship(back_populates="payments")


class ChannelAccess(Base, TimestampMixin):
    __tablename__ = "channel_access"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    subscription_id: Mapped[int] = mapped_column(ForeignKey("subscriptions.id"), nullable=False, index=True)
    invite_link: Mapped[str | None] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(32), nullable=False, index=True)
    expires_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)


class WebAccount(Base, TimestampMixin):
    __tablename__ = "web_accounts"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    phone: Mapped[str] = mapped_column(String(64), nullable=False)
    phone_normalized: Mapped[str] = mapped_column(String(16), unique=True, nullable=False, index=True)
    password_hash: Mapped[str | None] = mapped_column(Text)
    email_verification_token_hash: Mapped[str | None] = mapped_column(String(64), unique=True)
    email_verification_sent_at: Mapped[datetime | None] = mapped_column(DateTime)
    email_verification_expires_at: Mapped[datetime | None] = mapped_column(DateTime)
    email_verified_at: Mapped[datetime | None] = mapped_column(DateTime)
    temporary_password_sent_at: Mapped[datetime | None] = mapped_column(DateTime)
    password_reset_token_hash: Mapped[str | None] = mapped_column(String(64), unique=True)
    password_reset_sent_at: Mapped[datetime | None] = mapped_column(DateTime)
    password_reset_expires_at: Mapped[datetime | None] = mapped_column(DateTime)
    must_change_password: Mapped[bool] = mapped_column(Boolean, default=False, server_default="false", nullable=False)
    status: Mapped[str] = mapped_column(String(32), default="email_pending", server_default="email_pending", nullable=False, index=True)
    trial_used: Mapped[bool] = mapped_column(Boolean, default=False, server_default="false", nullable=False)
    last_login_at: Mapped[datetime | None] = mapped_column(DateTime)

    entitlement: Mapped["AccessEntitlement"] = relationship(back_populates="account", uselist=False)
    sessions: Mapped[list["WebSession"]] = relationship(back_populates="account")


class AccessEntitlement(Base, TimestampMixin):
    __tablename__ = "access_entitlements"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    account_id: Mapped[int] = mapped_column(ForeignKey("web_accounts.id"), unique=True, nullable=False, index=True)
    access_status: Mapped[str] = mapped_column(String(32), default="email_pending", server_default="email_pending", nullable=False, index=True)
    access_type: Mapped[str | None] = mapped_column(String(32))
    trial_start_at: Mapped[datetime | None] = mapped_column(DateTime)
    trial_end_at: Mapped[datetime | None] = mapped_column(DateTime)
    paid_start_at: Mapped[datetime | None] = mapped_column(DateTime)
    paid_end_at: Mapped[datetime | None] = mapped_column(DateTime)
    current_period_end: Mapped[datetime | None] = mapped_column(DateTime, index=True)
    revoked_at: Mapped[datetime | None] = mapped_column(DateTime)

    account: Mapped[WebAccount] = relationship(back_populates="entitlement")


class WebSession(Base, TimestampMixin):
    __tablename__ = "web_sessions"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    account_id: Mapped[int] = mapped_column(ForeignKey("web_accounts.id"), nullable=False, index=True)
    session_token_hash: Mapped[str] = mapped_column(String(64), unique=True, nullable=False, index=True)
    expires_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)
    revoked_at: Mapped[datetime | None] = mapped_column(DateTime, index=True)
    last_seen_at: Mapped[datetime | None] = mapped_column(DateTime)
    user_agent_hash: Mapped[str | None] = mapped_column(String(64))
    ip_hash: Mapped[str | None] = mapped_column(String(64))

    account: Mapped[WebAccount] = relationship(back_populates="sessions")


class AccountAuditEvent(Base):
    __tablename__ = "account_audit_events"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    account_id: Mapped[int | None] = mapped_column(ForeignKey("web_accounts.id"), index=True)
    event_type: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    occurred_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False, index=True)
    payload: Mapped[dict | None] = mapped_column(JSONB)


class Reminder(Base, TimestampMixin):
    __tablename__ = "reminders"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    subscription_id: Mapped[int] = mapped_column(ForeignKey("subscriptions.id"), nullable=False, index=True)
    type: Mapped[str] = mapped_column(String(32), nullable=False)
    send_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)
    sent_at: Mapped[datetime | None] = mapped_column(DateTime)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="pending")


class SiteEvent(Base):
    __tablename__ = "site_events"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    event_id: Mapped[str | None] = mapped_column(String(128), unique=True)
    event_type: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    occurred_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    received_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False, index=True)
    lead_id: Mapped[str | None] = mapped_column(String(128), index=True)
    session_id: Mapped[str | None] = mapped_column(String(128), index=True)
    client_id: Mapped[str | None] = mapped_column(String(128), index=True)
    yclid: Mapped[str | None] = mapped_column(String(128), index=True)
    payment_token: Mapped[str | None] = mapped_column(String(128), index=True)
    payment_id: Mapped[int | None] = mapped_column(ForeignKey("payments.id"), index=True)
    telegram_user_id: Mapped[int | None] = mapped_column(BigInteger, index=True)
    url: Mapped[str | None] = mapped_column(Text)
    referrer: Mapped[str | None] = mapped_column(Text)
    user_agent: Mapped[str | None] = mapped_column(Text)
    ip_address: Mapped[str | None] = mapped_column(String(45))
    attribution: Mapped[dict | None] = mapped_column(JSONB)
    payload: Mapped[dict | None] = mapped_column(JSONB)


class LeadAttribution(Base, TimestampMixin):
    __tablename__ = "lead_attribution"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    lead_id: Mapped[str | None] = mapped_column(String(128), unique=True)
    session_id: Mapped[str | None] = mapped_column(String(128), index=True)
    client_id: Mapped[str | None] = mapped_column(String(128), index=True)
    yclid: Mapped[str | None] = mapped_column(String(128), index=True)
    payment_token: Mapped[str | None] = mapped_column(String(128), unique=True)
    payment_id: Mapped[int | None] = mapped_column(ForeignKey("payments.id"), unique=True)
    telegram_user_id: Mapped[int | None] = mapped_column(BigInteger, index=True)
    utm_source: Mapped[str | None] = mapped_column(String(128), index=True)
    utm_medium: Mapped[str | None] = mapped_column(String(128))
    utm_campaign: Mapped[str | None] = mapped_column(String(255))
    utm_content: Mapped[str | None] = mapped_column(String(255))
    utm_term: Mapped[str | None] = mapped_column(String(255))
    first_url: Mapped[str | None] = mapped_column(Text)
    landing_url: Mapped[str | None] = mapped_column(Text)
    referrer: Mapped[str | None] = mapped_column(Text)
    first_seen_at: Mapped[datetime | None] = mapped_column(DateTime)
    last_seen_at: Mapped[datetime | None] = mapped_column(DateTime)
    source_payload: Mapped[dict | None] = mapped_column(JSONB)


class RawDirectReport(Base):
    __tablename__ = "raw_direct_reports"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    report_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    report_type: Mapped[str] = mapped_column(String(64), nullable=False)
    campaign_id: Mapped[str | None] = mapped_column(String(128), index=True)
    ad_group_id: Mapped[str | None] = mapped_column(String(128), index=True)
    ad_id: Mapped[str | None] = mapped_column(String(128), index=True)
    keyword_id: Mapped[str | None] = mapped_column(String(128), index=True)
    row_data: Mapped[dict] = mapped_column(JSONB, nullable=False)
    imported_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)


class RawMetricaLog(Base):
    __tablename__ = "raw_metrica_logs"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    log_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    source: Mapped[str] = mapped_column(String(64), nullable=False)
    client_id: Mapped[str | None] = mapped_column(String(128), index=True)
    yclid: Mapped[str | None] = mapped_column(String(128), index=True)
    visit_id: Mapped[str | None] = mapped_column(String(128), index=True)
    hit_id: Mapped[str | None] = mapped_column(String(128), index=True)
    row_data: Mapped[dict] = mapped_column(JSONB, nullable=False)
    imported_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)


class AnalyticsMartSnapshot(Base):
    __tablename__ = "analytics_mart_snapshots"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    snapshot_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    window_start: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    window_end: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    segment_id: Mapped[str] = mapped_column(String(128), nullable=False, index=True)
    metrics: Mapped[dict] = mapped_column(JSONB, nullable=False)
    source_refs: Mapped[dict | None] = mapped_column(JSONB)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)


class CodexDecision(Base, TimestampMixin):
    __tablename__ = "codex_decisions"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    decision_id: Mapped[str] = mapped_column(String(128), unique=True, nullable=False)
    segment_id: Mapped[str | None] = mapped_column(String(128), index=True)
    data_window: Mapped[dict | None] = mapped_column(JSONB)
    sample_size: Mapped[int | None] = mapped_column(Integer)
    reason_codes: Mapped[list] = mapped_column(JSONB, nullable=False)
    proposed_action: Mapped[str | None] = mapped_column(String(64), index=True)
    change_value: Mapped[dict | None] = mapped_column(JSONB)
    confidence: Mapped[Decimal | None] = mapped_column(Numeric(5, 4))
    rollback_plan: Mapped[dict | None] = mapped_column(JSONB)
    compliance_flag: Mapped[bool] = mapped_column(Boolean, default=False, server_default="false", nullable=False)
    status: Mapped[str] = mapped_column(String(32), default="pending", server_default="pending", nullable=False, index=True)
    validation_errors: Mapped[list | None] = mapped_column(JSONB)


class CampaignSnapshot(Base):
    __tablename__ = "campaign_snapshots"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    snapshot_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)
    provider: Mapped[str] = mapped_column(String(64), default="yandex_direct", server_default="yandex_direct", nullable=False)
    campaign_id: Mapped[str | None] = mapped_column(String(128), index=True)
    ad_group_id: Mapped[str | None] = mapped_column(String(128), index=True)
    ad_id: Mapped[str | None] = mapped_column(String(128), index=True)
    keyword_id: Mapped[str | None] = mapped_column(String(128), index=True)
    state: Mapped[dict] = mapped_column(JSONB, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)


class ActionLog(Base, TimestampMixin):
    __tablename__ = "action_log"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    action_id: Mapped[str] = mapped_column(String(128), unique=True, nullable=False)
    decision_id: Mapped[str | None] = mapped_column(ForeignKey("codex_decisions.decision_id"))
    proposed_action: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    target_type: Mapped[str | None] = mapped_column(String(64))
    target_id: Mapped[str | None] = mapped_column(String(128), index=True)
    dry_run: Mapped[bool] = mapped_column(Boolean, default=True, server_default="true", nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False, index=True)
    previous_state: Mapped[dict | None] = mapped_column(JSONB)
    new_state: Mapped[dict | None] = mapped_column(JSONB)
    rollback_payload: Mapped[dict | None] = mapped_column(JSONB)
    error_message: Mapped[str | None] = mapped_column(Text)
    executed_at: Mapped[datetime | None] = mapped_column(DateTime)


class Alert(Base, TimestampMixin):
    __tablename__ = "alerts"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    alert_key: Mapped[str] = mapped_column(String(160), unique=True, nullable=False)
    severity: Mapped[str] = mapped_column(String(16), nullable=False, index=True)
    alert_type: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    status: Mapped[str] = mapped_column(String(32), default="open", server_default="open", nullable=False, index=True)
    payload: Mapped[dict] = mapped_column(JSONB, nullable=False)
    resolved_at: Mapped[datetime | None] = mapped_column(DateTime)


Index("ix_payments_pending_token", Payment.payment_token, Payment.status)
Index("ix_payments_client_yclid", Payment.client_id, Payment.yclid)
Index("ix_subscriptions_user_status_end", Subscription.user_id, Subscription.status, Subscription.end_date)
Index("ix_access_entitlements_status_end", AccessEntitlement.access_status, AccessEntitlement.current_period_end)
Index("ix_site_events_type_occurred", SiteEvent.event_type, SiteEvent.occurred_at)
Index("ix_lead_attribution_client_yclid", LeadAttribution.client_id, LeadAttribution.yclid)
Index("ix_raw_direct_reports_type_date", RawDirectReport.report_type, RawDirectReport.report_date)
Index("ix_raw_metrica_logs_source_date", RawMetricaLog.source, RawMetricaLog.log_date)
Index("ix_analytics_mart_segment_window", AnalyticsMartSnapshot.segment_id, AnalyticsMartSnapshot.window_start, AnalyticsMartSnapshot.window_end)
Index("ix_campaign_snapshots_campaign_time", CampaignSnapshot.campaign_id, CampaignSnapshot.snapshot_at)
