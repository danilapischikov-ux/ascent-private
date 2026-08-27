from decimal import Decimal
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import create_payment_token, utcnow
from app.db.models import Payment


async def create_pending_payment(
    session: AsyncSession,
    *,
    user_id: int,
    telegram_user_id: int,
    amount: Decimal,
    currency: str,
) -> Payment:
    payment = Payment(
        user_id=user_id,
        telegram_user_id=telegram_user_id,
        payment_token=create_payment_token(),
        status="pending",
        amount=amount,
        currency=currency,
    )
    session.add(payment)
    await session.flush()
    payment.inv_id = payment.id
    await session.flush()
    return payment


async def get_by_token(session: AsyncSession, payment_token: str) -> Payment | None:
    result = await session.execute(select(Payment).where(Payment.payment_token == payment_token))
    return result.scalar_one_or_none()


async def get_by_inv_id(session: AsyncSession, inv_id: int) -> Payment | None:
    result = await session.execute(select(Payment).where(Payment.inv_id == inv_id))
    return result.scalar_one_or_none()


async def get_by_inv_id_for_update(session: AsyncSession, inv_id: int) -> Payment | None:
    result = await session.execute(select(Payment).where(Payment.inv_id == inv_id).with_for_update())
    return result.scalar_one_or_none()


async def get_by_provider_payment_id_for_update(
    session: AsyncSession,
    provider_payment_id: str,
) -> Payment | None:
    result = await session.execute(
        select(Payment).where(Payment.provider_payment_id == provider_payment_id).with_for_update()
    )
    return result.scalar_one_or_none()


async def attach_customer_data(
    session: AsyncSession,
    payment: Payment,
    *,
    name: str,
    email: str,
    phone: str,
    lead_id: str | None = None,
    session_id: str | None = None,
    client_id: str | None = None,
    yclid: str | None = None,
    attribution: dict[str, Any] | None = None,
) -> Payment:
    payment.customer_name = name
    payment.customer_email = email
    payment.customer_phone = phone
    payment.lead_id = lead_id
    payment.session_id = session_id
    payment.client_id = client_id
    payment.yclid = yclid
    payment.attribution = attribution
    await session.flush()
    return payment


async def attach_provider_payment(
    session: AsyncSession,
    payment: Payment,
    *,
    provider: str,
    provider_payment_id: str,
    provider_status: str,
    provider_confirmation_url: str | None,
    provider_created_payload: dict[str, Any],
) -> Payment:
    payment.provider = provider
    payment.provider_payment_id = provider_payment_id
    payment.provider_status = provider_status
    payment.provider_confirmation_url = provider_confirmation_url
    payment.provider_created_payload = provider_created_payload
    await session.flush()
    return payment


async def attach_provider_webhook(
    session: AsyncSession,
    payment: Payment,
    *,
    provider_status: str,
    provider_webhook_payload: dict[str, Any],
) -> Payment:
    payment.provider_status = provider_status
    payment.provider_webhook_payload = provider_webhook_payload
    await session.flush()
    return payment


async def mark_paid_once(session: AsyncSession, payment: Payment, raw_result: dict) -> bool:
    if payment.status == "paid":
        return False
    payment.status = "paid"
    payment.paid_at = utcnow()
    payment.raw_result = raw_result
    await session.flush()
    return True
