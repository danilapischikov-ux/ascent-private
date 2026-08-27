import logging

import httpx
from aiogram.types import User as TelegramUser

from app.core.config import Settings
from app.core.security import utcnow

logger = logging.getLogger(__name__)


async def send_client_funnel_event(settings: Settings, payload: dict[str, str | int]) -> None:
    endpoint = getattr(settings, "payment_report_sheets_endpoint", "")
    if not endpoint:
        return

    try:
        async with httpx.AsyncClient(timeout=10, follow_redirects=True) as client:
            response = await client.post(endpoint, json=payload)
            response.raise_for_status()
    except Exception:
        logger.exception("Failed to send client funnel event")


async def send_faq_question_to_funnel(
    settings: Settings,
    telegram_user: TelegramUser | None,
    question: str,
) -> None:
    if telegram_user is None:
        return

    await send_client_funnel_event(
        settings,
        {
            "eventType": "faq_question",
            "telegramUserId": telegram_user.id,
            "telegramUsername": telegram_user.username or "",
            "firstName": telegram_user.first_name or "",
            "lastName": telegram_user.last_name or "",
            "question": question,
            "askedAt": utcnow().isoformat(),
            "source": "faq_site",
        },
    )


async def send_faq_start_to_funnel(settings: Settings, telegram_user: TelegramUser | None) -> None:
    if telegram_user is None:
        return

    await send_client_funnel_event(
        settings,
        {
            "eventType": "faq_started",
            "telegramUserId": telegram_user.id,
            "telegramUsername": telegram_user.username or "",
            "firstName": telegram_user.first_name or "",
            "lastName": telegram_user.last_name or "",
            "startedAt": utcnow().isoformat(),
            "source": "faq_site",
        },
    )
