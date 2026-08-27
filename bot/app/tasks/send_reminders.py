from aiogram import Bot
from sqlalchemy.ext.asyncio import AsyncSession

from app.bot.messages.reminders import ACCESS_EXPIRES_SOON_TEXT
from app.core.security import utcnow
from app.db.models import User
from app.db.repositories.reminders import list_due


async def send_due_reminders_job(session: AsyncSession, bot: Bot) -> None:
    reminders = await list_due(session, utcnow())
    for reminder in reminders:
        user = await session.get(User, reminder.user_id)
        if user is None:
            reminder.status = "skipped"
            continue
        await bot.send_message(user.telegram_user_id, ACCESS_EXPIRES_SOON_TEXT)
        reminder.status = "sent"
        reminder.sent_at = utcnow()
    await session.commit()
