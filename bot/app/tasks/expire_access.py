import logging

from aiogram import Bot
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import Settings
from app.core.security import utcnow
from app.db.models import User
from app.db.repositories.subscriptions import get_active_for_user, list_expired_active
from app.services.channel_access import expire_channel_access
from app.services.support_chat import notify_support_chat

logger = logging.getLogger(__name__)


async def expire_access_job(session: AsyncSession, settings: Settings, bot: Bot) -> None:
    now = utcnow()
    subscriptions = await list_expired_active(session, now)
    for subscription in subscriptions:
        user = await session.get(User, subscription.user_id)
        if user is None:
            continue
        subscription.status = "expired"
        next_active = await get_active_for_user(session, user.id)
        if next_active and next_active.id != subscription.id and next_active.end_date > now:
            continue
        await expire_channel_access(settings, bot, user)
        await notify_support_chat(
            settings,
            bot,
            f"Доступ завершен: {user.telegram_user_id} @{user.username or '-'}",
        )
    await session.commit()
