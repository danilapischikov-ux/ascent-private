import logging
from datetime import timedelta

from aiogram import Bot
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import Settings
from app.db.models import Subscription, User
from app.db.repositories import channel_access as access_repo

logger = logging.getLogger(__name__)


async def issue_channel_access(
    session: AsyncSession,
    settings: Settings,
    bot: Bot,
    *,
    user: User,
    subscription: Subscription,
) -> str | None:
    invite_link: str | None = None
    try:
        await bot.unban_chat_member(settings.telegram_channel_id, user.telegram_user_id, only_if_banned=True)
        invite = await bot.create_chat_invite_link(
            chat_id=settings.telegram_channel_id,
            member_limit=1,
            expire_date=subscription.end_date - timedelta(minutes=5),
            name=f"ascent-{user.telegram_user_id}-{subscription.id}",
        )
        invite_link = invite.invite_link
        await bot.send_message(
            user.telegram_user_id,
            "Доступ готов. Ваша индивидуальная ссылка в закрытый канал:\n"
            f"{invite_link}\n\n"
            f"Ссылка действует до {subscription.end_date:%d.%m.%Y}.",
        )
    except Exception:
        logger.exception("Failed to issue channel access for user %s", user.telegram_user_id)

    await access_repo.create_access(
        session,
        user_id=user.id,
        subscription_id=subscription.id,
        invite_link=invite_link,
        expires_at=subscription.end_date,
    )
    return invite_link


async def expire_channel_access(settings: Settings, bot: Bot, user: User) -> None:
    try:
        await bot.ban_chat_member(settings.telegram_channel_id, user.telegram_user_id)
        await bot.send_message(
            user.telegram_user_id,
            "Ваш доступ к Ascent Private завершился. Для продления нажмите кнопку оплаты в боте.",
        )
    except Exception:
        logger.exception("Failed to expire channel access for user %s", user.telegram_user_id)
