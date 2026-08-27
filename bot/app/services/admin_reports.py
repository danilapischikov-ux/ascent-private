import asyncio
import logging
from decimal import Decimal

from aiogram import Bot
import httpx
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import Settings
from app.core.security import utcnow
from app.db.models import Payment, Subscription, User
from app.services.email import send_email
from app.services.support_chat import notify_support_chat

logger = logging.getLogger(__name__)


def build_payment_report(payment: Payment, user: User, subscription: Subscription) -> str:
    return "\n".join(
        [
            "Новая оплата Ascent Private",
            "",
            f"Имя: {payment.customer_name or '-'}",
            f"Email: {payment.customer_email or '-'}",
            f"Телефон: {payment.customer_phone or '-'}",
            f"Telegram ID: {user.telegram_user_id}",
            f"Telegram username: @{user.username}" if user.username else "Telegram username: -",
            f"Сумма: {Decimal(payment.amount):.2f} {payment.currency}",
            f"Дата оплаты: {payment.paid_at:%d.%m.%Y %H:%M:%S}" if payment.paid_at else "Дата оплаты: -",
            f"Срок подписки: {subscription.type}, {subscription.start_date:%d.%m.%Y} - {subscription.end_date:%d.%m.%Y}",
            f"Дата окончания доступа: {subscription.end_date:%d.%m.%Y}",
            f"Платёжный провайдер: {payment.provider or 'robokassa'}",
            f"ID платежа провайдера: {payment.provider_payment_id or '-'}",
            f"InvId Robokassa: {payment.inv_id}",
        ],
    )


def build_payment_sheets_payload(payment: Payment, user: User, subscription: Subscription) -> dict[str, str | int]:
    return {
        "eventType": "payment_paid",
        "telegramUserId": user.telegram_user_id,
        "telegramUsername": user.username or "",
        "firstName": user.first_name or "",
        "lastName": user.last_name or "",
        "customerName": payment.customer_name or "",
        "customerEmail": payment.customer_email or "",
        "customerPhone": payment.customer_phone or "",
        "amount": f"{Decimal(payment.amount):.2f}",
        "currency": payment.currency,
        "paymentToken": payment.payment_token,
        "paymentProvider": payment.provider or "robokassa",
        "providerPaymentId": payment.provider_payment_id or "",
        "robokassaInvId": payment.inv_id or "",
        "paidAt": payment.paid_at.isoformat() if payment.paid_at else "",
        "activatedAt": payment.activated_at.isoformat() if payment.activated_at else "",
        "subscriptionType": subscription.type,
        "subscriptionStartedAt": subscription.start_date.isoformat(),
        "subscriptionEndsAt": subscription.end_date.isoformat(),
    }


async def send_payment_report_to_sheets(settings: Settings, payment: Payment, user: User, subscription: Subscription) -> None:
    endpoint = getattr(settings, "payment_report_sheets_endpoint", "")
    if not endpoint:
        return

    payload = build_payment_sheets_payload(payment, user, subscription)
    try:
        async with httpx.AsyncClient(timeout=10, follow_redirects=True) as client:
            response = await client.post(endpoint, json=payload)
            response.raise_for_status()
    except Exception:
        logger.exception("Failed to send payment report to Google Sheets")


async def send_payment_reports_once(
    session: AsyncSession,
    settings: Settings,
    bot: Bot,
    *,
    payment: Payment,
    user: User,
    subscription: Subscription,
) -> None:
    if payment.report_sent_at:
        return

    report = build_payment_report(payment, user, subscription)
    if settings.payment_report_email_enabled:
        try:
            await asyncio.to_thread(
                send_email,
                settings,
                to_email=settings.payment_report_email_to,
                subject=settings.payment_report_email_subject,
                body=report,
            )
        except Exception:
            logger.exception("Failed to send payment report email")

    await notify_support_chat(settings, bot, report)
    await send_payment_report_to_sheets(settings, payment, user, subscription)
    payment.report_sent_at = utcnow()
    await session.flush()
