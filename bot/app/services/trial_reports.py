import logging

import httpx

from app.core.config import Settings
from app.db.models import Subscription, User

logger = logging.getLogger(__name__)


def build_trial_report_payload(user: User, subscription: Subscription) -> dict[str, str | int]:
    return {
        "telegramUserId": user.telegram_user_id,
        "telegramUsername": user.username or "",
        "firstName": user.first_name or "",
        "lastName": user.last_name or "",
        "source": user.source or "",
        "subscriptionId": subscription.id,
        "trialStartedAt": subscription.start_date.isoformat(),
        "trialEndsAt": subscription.end_date.isoformat(),
    }


async def send_trial_report_to_sheets(settings: Settings, user: User, subscription: Subscription) -> None:
    if not settings.trial_report_sheets_endpoint:
        return

    payload = build_trial_report_payload(user, subscription)
    try:
        async with httpx.AsyncClient(timeout=10, follow_redirects=True) as client:
            response = await client.post(settings.trial_report_sheets_endpoint, json=payload)
            response.raise_for_status()
    except Exception:
        logger.exception("Failed to send trial report to Google Sheets")
