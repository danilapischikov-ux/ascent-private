from decimal import Decimal, InvalidOperation
import logging
from typing import Any

from aiogram import Bot
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.db.models import User
from app.db.repositories import analytics as analytics_repo
from app.db.repositories import payments as payment_repo
from app.db.session import get_db_session
from app.services.admin_reports import send_payment_reports_once
from app.services.channel_access import issue_channel_access
from app.services.subscriptions import activate_paid_subscription
from app.services.yookassa_payments import YooKassaApiError, YooKassaPaymentResult, get_yookassa_payment

router = APIRouter(tags=["yookassa"])
logger = logging.getLogger(__name__)


def _provider_payment_id(payload: dict[str, Any]) -> str | None:
    payment = payload.get("object")
    if not isinstance(payment, dict):
        return None
    payment_id = payment.get("id")
    return payment_id if isinstance(payment_id, str) and payment_id else None


def _verified_payment_matches_local(payment_id: str, payment, result: YooKassaPaymentResult) -> bool:
    try:
        amount_matches = Decimal(result.amount) == Decimal(payment.amount)
    except (InvalidOperation, ValueError):
        return False

    return (
        result.provider_payment_id == payment_id
        and amount_matches
        and result.currency == payment.currency
        and result.metadata.get("payment_id") == str(payment.id)
        and result.metadata.get("payment_token") == payment.payment_token
        and result.metadata.get("telegram_user_id") == str(payment.telegram_user_id)
    )


@router.post("/yookassa/webhook")
async def yookassa_webhook(
    request: Request,
    session: AsyncSession = Depends(get_db_session),
) -> dict[str, bool | str]:
    try:
        payload = await request.json()
    except ValueError as error:
        raise HTTPException(status_code=400, detail="Invalid YooKassa webhook JSON") from error

    if not isinstance(payload, dict):
        raise HTTPException(status_code=400, detail="Invalid YooKassa webhook payload")

    event = payload.get("event")
    if event not in {"payment.succeeded", "payment.canceled"}:
        return {"ok": True, "status": "ignored"}

    provider_payment_id = _provider_payment_id(payload)
    if provider_payment_id is None:
        raise HTTPException(status_code=400, detail="YooKassa webhook payment id is missing")

    payment = await payment_repo.get_by_provider_payment_id_for_update(session, provider_payment_id)
    if payment is None or payment.provider != "yookassa":
        logger.warning("YooKassa webhook payment not found provider_payment_id=%s", provider_payment_id)
        return {"ok": True, "status": "ignored"}

    settings = get_settings()
    try:
        result = await get_yookassa_payment(settings, provider_payment_id)
    except YooKassaApiError as error:
        raise HTTPException(status_code=503, detail="Unable to verify YooKassa payment") from error

    await payment_repo.attach_provider_webhook(
        session,
        payment,
        provider_status=result.status,
        provider_webhook_payload=payload,
    )

    if event == "payment.canceled":
        await session.commit()
        return {"ok": True, "status": "canceled"}

    if result.status != "succeeded" or not _verified_payment_matches_local(provider_payment_id, payment, result):
        logger.warning("YooKassa webhook verification failed provider_payment_id=%s", provider_payment_id)
        await session.commit()
        return {"ok": True, "status": "ignored"}

    changed = await payment_repo.mark_paid_once(session, payment, raw_result=result.payload)
    await analytics_repo.record_payment_confirmed(session, payment, result.payload)
    if changed or payment.activated_at is None:
        user = await session.get(User, payment.user_id)
        if user is None:
            raise HTTPException(status_code=404, detail="User not found")
        subscription = await activate_paid_subscription(session, settings, user, payment)
        bot: Bot = request.app.state.bot
        await issue_channel_access(session, settings, bot, user=user, subscription=subscription)
        await send_payment_reports_once(session, settings, bot, payment=payment, user=user, subscription=subscription)
    await session.commit()
    return {"ok": True, "status": "succeeded"}
