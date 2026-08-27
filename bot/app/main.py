from contextlib import asynccontextmanager
import asyncio
import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import auth, events, health, payments, robokassa, telegram_webhook, yookassa
from app.bot.bot import create_bot
from app.bot.dispatcher import create_dispatcher
from app.core.config import get_settings
from app.core.logging import configure_logging
from app.tasks.scheduler import create_scheduler

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    configure_logging()
    settings = get_settings()
    bot = create_bot()
    dispatcher = create_dispatcher()
    scheduler = create_scheduler(settings, bot)
    app.state.bot = bot
    app.state.dispatcher = dispatcher
    app.state.scheduler = scheduler

    if settings.telegram_webhook_url:
        try:
            await asyncio.wait_for(
                bot.set_webhook(
                    settings.telegram_webhook_url,
                    secret_token=settings.telegram_webhook_secret or None,
                ),
                timeout=10,
            )
        except Exception:
            logger.exception("Failed to set Telegram webhook; application will continue running")
    scheduler.start()
    try:
        yield
    finally:
        scheduler.shutdown(wait=False)
        await bot.session.close()


settings = get_settings()
app = FastAPI(title="Ascent Private Bot API", version="1.0.0", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization", "X-Requested-With"],
)
app.include_router(health.router)
app.include_router(auth.router)
app.include_router(telegram_webhook.router)
app.include_router(events.router)
app.include_router(payments.router)
app.include_router(robokassa.router)
app.include_router(yookassa.router)
