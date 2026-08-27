import logging

from aiogram import Bot
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from app.core.config import Settings
from app.db.session import async_session_maker
from app.tasks.expire_access import expire_access_job
from app.tasks.send_reminders import send_due_reminders_job

logger = logging.getLogger(__name__)


async def _expire_access(settings: Settings, bot: Bot) -> None:
    async with async_session_maker() as session:
        await expire_access_job(session, settings, bot)


async def _send_reminders(bot: Bot) -> None:
    async with async_session_maker() as session:
        await send_due_reminders_job(session, bot)


def create_scheduler(settings: Settings, bot: Bot) -> AsyncIOScheduler:
    scheduler = AsyncIOScheduler(timezone="UTC")
    scheduler.add_job(_expire_access, "interval", minutes=30, args=[settings, bot], id="expire_access")
    scheduler.add_job(_send_reminders, "interval", minutes=15, args=[bot], id="send_reminders")
    return scheduler
