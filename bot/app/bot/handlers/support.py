from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from app.bot.messages.support import SUPPORT_TEXT

router = Router()


@router.message(Command("support"))
async def handle_support(message: Message) -> None:
    await message.answer(SUPPORT_TEXT)
