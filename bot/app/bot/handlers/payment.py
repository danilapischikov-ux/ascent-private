from decimal import Decimal

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from app.bot.handlers.start import payment_page_url
from app.bot.keyboards import payment_keyboard
from app.bot.messages.payment import PAYMENT_GENERIC_TEXT
from app.core.config import get_settings
from app.db.repositories import payments as payment_repo
from app.db.repositories import users as user_repo
from app.db.session import async_session_maker

router = Router()


@router.message(Command("pay"))
async def handle_pay(message: Message) -> None:
    if message.from_user is None:
        return
    settings = get_settings()
    async with async_session_maker() as session:
        user = await user_repo.upsert_from_telegram(session, message.from_user, source="pay_command")
        payment = await payment_repo.create_pending_payment(
            session,
            user_id=user.id,
            telegram_user_id=user.telegram_user_id,
            amount=Decimal(settings.subscription_rub_price),
            currency=settings.currency_code,
        )
        await session.commit()
    await message.answer(PAYMENT_GENERIC_TEXT, reply_markup=payment_keyboard(payment_page_url(payment.payment_token)))
