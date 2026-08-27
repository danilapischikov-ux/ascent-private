from datetime import UTC, datetime
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import utcnow
from app.db.models import LeadAttribution, Payment, SiteEvent


UTM_FIELDS = ("utm_source", "utm_medium", "utm_campaign", "utm_content", "utm_term")


def _clean(value: str | None) -> str | None:
    if value is None:
        return None
    stripped = value.strip()
    return stripped or None


def _read_attribution(attribution: dict[str, Any] | None, key: str) -> str | None:
    if not attribution:
        return None
    value = attribution.get(key)
    return _clean(str(value)) if value is not None else None


def _normalize_datetime(value: datetime | None) -> datetime:
    if value is None:
        return utcnow()
    if value.tzinfo is None:
        return value
    return value.astimezone(UTC).replace(tzinfo=None)


async def _find_lead_attribution(
    session: AsyncSession,
    *,
    lead_id: str | None = None,
    session_id: str | None = None,
    payment_token: str | None = None,
    payment_id: int | None = None,
    client_id: str | None = None,
    yclid: str | None = None,
) -> LeadAttribution | None:
    if payment_id is not None:
        result = await session.execute(select(LeadAttribution).where(LeadAttribution.payment_id == payment_id))
        found = result.scalars().first()
        if found is not None:
            return found
    if payment_token:
        result = await session.execute(select(LeadAttribution).where(LeadAttribution.payment_token == payment_token))
        found = result.scalars().first()
        if found is not None:
            return found
    if lead_id:
        result = await session.execute(select(LeadAttribution).where(LeadAttribution.lead_id == lead_id))
        found = result.scalars().first()
        if found is not None:
            return found
    if session_id:
        result = await session.execute(select(LeadAttribution).where(LeadAttribution.session_id == session_id).limit(1))
        found = result.scalars().first()
        if found is not None:
            return found
    if client_id and yclid:
        result = await session.execute(
            select(LeadAttribution).where(
                LeadAttribution.client_id == client_id,
                LeadAttribution.yclid == yclid,
            ).limit(1),
        )
        return result.scalars().first()
    return None


async def upsert_lead_attribution(
    session: AsyncSession,
    *,
    lead_id: str | None = None,
    session_id: str | None = None,
    client_id: str | None = None,
    yclid: str | None = None,
    payment_token: str | None = None,
    payment_id: int | None = None,
    telegram_user_id: int | None = None,
    attribution: dict[str, Any] | None = None,
    url: str | None = None,
    referrer: str | None = None,
    occurred_at: datetime | None = None,
) -> LeadAttribution | None:
    lead_id = _clean(lead_id)
    session_id = _clean(session_id)
    client_id = _clean(client_id)
    yclid = _clean(yclid)
    payment_token = _clean(payment_token)
    if not any((lead_id, session_id, client_id, yclid, payment_token, payment_id, telegram_user_id)):
        return None

    now = _normalize_datetime(occurred_at)
    record = await _find_lead_attribution(
        session,
        lead_id=lead_id,
        session_id=session_id,
        payment_token=payment_token,
        payment_id=payment_id,
        client_id=client_id,
        yclid=yclid,
    )
    if record is None:
        record = LeadAttribution(
            lead_id=lead_id,
            session_id=session_id,
            client_id=client_id,
            yclid=yclid,
            payment_token=payment_token,
            payment_id=payment_id,
            telegram_user_id=telegram_user_id,
            first_url=url,
            landing_url=url,
            referrer=referrer,
            first_seen_at=now,
            last_seen_at=now,
            source_payload=attribution,
        )
        session.add(record)
    else:
        record.lead_id = record.lead_id or lead_id
        record.session_id = record.session_id or session_id
        record.client_id = record.client_id or client_id
        record.yclid = record.yclid or yclid
        record.payment_token = record.payment_token or payment_token
        record.payment_id = record.payment_id or payment_id
        record.telegram_user_id = record.telegram_user_id or telegram_user_id
        record.first_url = record.first_url or url
        record.landing_url = record.landing_url or url
        record.referrer = record.referrer or referrer
        record.first_seen_at = record.first_seen_at or now
        record.last_seen_at = now
        if attribution:
            record.source_payload = {**(record.source_payload or {}), **attribution}

    for field in UTM_FIELDS:
        value = _read_attribution(attribution, field)
        if value:
            setattr(record, field, getattr(record, field) or value)

    await session.flush()
    return record


async def create_site_event(
    session: AsyncSession,
    *,
    event_type: str,
    event_id: str | None = None,
    occurred_at: datetime | None = None,
    lead_id: str | None = None,
    session_id: str | None = None,
    client_id: str | None = None,
    yclid: str | None = None,
    payment_token: str | None = None,
    payment_id: int | None = None,
    telegram_user_id: int | None = None,
    url: str | None = None,
    referrer: str | None = None,
    user_agent: str | None = None,
    ip_address: str | None = None,
    attribution: dict[str, Any] | None = None,
    payload: dict[str, Any] | None = None,
) -> tuple[SiteEvent, bool]:
    event_id = _clean(event_id)
    if event_id:
        result = await session.execute(select(SiteEvent).where(SiteEvent.event_id == event_id))
        existing = result.scalar_one_or_none()
        if existing is not None:
            return existing, False

    event = SiteEvent(
        event_id=event_id,
        event_type=event_type,
        occurred_at=_normalize_datetime(occurred_at),
        lead_id=_clean(lead_id),
        session_id=_clean(session_id),
        client_id=_clean(client_id),
        yclid=_clean(yclid),
        payment_token=_clean(payment_token),
        payment_id=payment_id,
        telegram_user_id=telegram_user_id,
        url=url,
        referrer=referrer,
        user_agent=user_agent,
        ip_address=ip_address,
        attribution=attribution,
        payload=payload,
    )
    session.add(event)
    await upsert_lead_attribution(
        session,
        lead_id=lead_id,
        session_id=session_id,
        client_id=client_id,
        yclid=yclid,
        payment_token=payment_token,
        payment_id=payment_id,
        telegram_user_id=telegram_user_id,
        attribution=attribution,
        url=url,
        referrer=referrer,
        occurred_at=event.occurred_at,
    )
    await session.flush()
    return event, True


async def record_payment_confirmed(session: AsyncSession, payment: Payment, raw_result: dict[str, str]) -> SiteEvent:
    attribution = payment.attribution or {}
    event, _ = await create_site_event(
        session,
        event_id=f"payment_confirmed:{payment.id}",
        event_type="payment_confirmed",
        occurred_at=payment.paid_at or utcnow(),
        lead_id=payment.lead_id,
        session_id=payment.session_id,
        client_id=payment.client_id,
        yclid=payment.yclid,
        payment_token=payment.payment_token,
        payment_id=payment.id,
        telegram_user_id=payment.telegram_user_id,
        attribution=attribution,
        payload={
            "amount": str(payment.amount),
            "currency": payment.currency,
            "inv_id": payment.inv_id,
            "robokassa": raw_result,
        },
    )
    return event
