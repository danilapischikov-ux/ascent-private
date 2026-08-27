import logging

from aiogram import Bot, Dispatcher
from aiogram.types import Update
from fastapi import APIRouter, BackgroundTasks, Header, HTTPException, Request

from app.core.config import get_settings

router = APIRouter(tags=["telegram"])
logger = logging.getLogger(__name__)


async def _feed_update_safely(bot: Bot, dispatcher: Dispatcher, update: Update) -> None:
    try:
        await dispatcher.feed_update(bot, update)
    except Exception:
        logger.exception("Failed to process Telegram update %s", update.update_id)


@router.post("/telegram/webhook")
async def telegram_webhook(
    request: Request,
    background_tasks: BackgroundTasks,
    x_telegram_bot_api_secret_token: str | None = Header(default=None),
) -> dict[str, bool]:
    settings = get_settings()
    if settings.telegram_webhook_secret and x_telegram_bot_api_secret_token != settings.telegram_webhook_secret:
        raise HTTPException(status_code=403, detail="Invalid Telegram webhook secret")

    bot: Bot = request.app.state.bot
    dispatcher: Dispatcher = request.app.state.dispatcher
    payload = await request.json()
    update = Update.model_validate(payload, context={"bot": bot})
    background_tasks.add_task(_feed_update_safely, bot, dispatcher, update)
    return {"ok": True}
