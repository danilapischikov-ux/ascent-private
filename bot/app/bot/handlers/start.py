from decimal import Decimal

from aiogram import Router
from aiogram.filters import CommandObject, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from app.bot.handlers.faq import begin_faq_dialog
from app.bot.keyboards import payment_keyboard
from app.bot.messages.payment import PAYMENT_TOKEN_CREATED_TEXT
from app.bot.messages.trial import TRIAL_ALREADY_USED_TEXT, TRIAL_STARTED_TEXT
from app.core.config import get_settings
from app.db.repositories import payments as payment_repo
from app.db.repositories import users as user_repo
from app.db.session import async_session_maker
from app.services.channel_access import issue_channel_access
from app.services.subscriptions import activate_trial
from app.services.support_chat import notify_support_chat
from app.services.trial_reports import send_trial_report_to_sheets

router = Router()


def payment_page_url(payment_token: str) -> str:
    settings = get_settings()
    return f"{settings.site_url}/?payment_token={payment_token}{settings.payment_form_anchor}"


@router.message(CommandStart())
async def handle_start(message: Message, command: CommandObject, state: FSMContext) -> None:
    settings = get_settings()
    source = command.args
    if message.from_user is None:
        return

    async with async_session_maker() as session:
        user = await user_repo.upsert_from_telegram(session, message.from_user, source=source)

        if source == settings.bot_trial_start_param:
            if user.trial_used and not settings.allow_repeat_trial_for_testing:
                payment = await payment_repo.create_pending_payment(
                    session,
                    user_id=user.id,
                    telegram_user_id=user.telegram_user_id,
                    amount=Decimal(settings.subscription_rub_price),
                    currency=settings.currency_code,
                )
                await session.commit()
                await message.answer(
                    TRIAL_ALREADY_USED_TEXT,
                    reply_markup=payment_keyboard(payment_page_url(payment.payment_token)),
                )
                return

            subscription = await activate_trial(session, settings, user)
            await session.commit()
            await message.answer(TRIAL_STARTED_TEXT)
            await issue_channel_access(session, settings, message.bot, user=user, subscription=subscription)
            await notify_support_chat(
                settings,
                message.bot,
                f"Trial активирован: {user.telegram_user_id} @{user.username or '-'}",
            )
            await send_trial_report_to_sheets(settings, user, subscription)
            await session.commit()
            return

        if source == settings.bot_payment_start_param:
            payment = await payment_repo.create_pending_payment(
                session,
                user_id=user.id,
                telegram_user_id=user.telegram_user_id,
                amount=Decimal(settings.subscription_rub_price),
                currency=settings.currency_code,
            )
            await session.commit()
            await message.answer(
                PAYMENT_TOKEN_CREATED_TEXT,
                reply_markup=payment_keyboard(payment_page_url(payment.payment_token)),
            )
            return

        if source == settings.bot_faq_start_param:
            await session.commit()
            await begin_faq_dialog(message, state)
            return

        await session.commit()

    await begin_faq_dialog(message, state)
