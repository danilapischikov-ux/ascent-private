from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from app.core.config import get_settings

router = Router()


@router.message(Command("health"))
async def handle_health(message: Message) -> None:
    settings = get_settings()
    if message.from_user is None or message.from_user.id not in settings.bot_admin_ids:
        return
    await message.answer("OK")
