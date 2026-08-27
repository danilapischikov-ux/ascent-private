import asyncio
import logging

from aiogram import Bot
from aiogram.exceptions import TelegramNetworkError

from app.core.config import Settings

logger = logging.getLogger(__name__)


async def notify_support_chat(settings: Settings, bot: Bot, text: str) -> bool:
    for attempt in range(1, 4):
        try:
            await bot.send_message(settings.telegram_support_chat_id, text)
            return True
        except TelegramNetworkError:
            if attempt == 3:
                logger.exception(
                    "Failed to send support chat notification to chat %s after %s attempts",
                    settings.telegram_support_chat_id,
                    attempt,
                )
                return False

            logger.warning(
                "Telegram network error sending support chat notification to chat %s; retry %s of 3",
                settings.telegram_support_chat_id,
                attempt,
            )
            await asyncio.sleep(attempt)
        except Exception:
            logger.exception(
                "Failed to send support chat notification to chat %s",
                settings.telegram_support_chat_id,
            )
            return False

    return False
