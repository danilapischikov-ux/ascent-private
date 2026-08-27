import logging
import re
from html import escape

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message, User

from app.bot.faq_search import FaqMatch, find_faq_matches
from app.bot.keyboards import FAQ_HELPFUL_NO, FAQ_HELPFUL_YES, faq_helpful_keyboard
from app.core.config import get_settings
from app.services.client_funnel_reports import send_faq_question_to_funnel, send_faq_start_to_funnel
from app.services.support_chat import notify_support_chat

router = Router()
logger = logging.getLogger(__name__)
FAQ_SUPPORT_QUEUED_TEXT = "Ваш вопрос отправлен Администратору. Вам ответят в ближайшее время"
FAQ_SUPPORT_DELIVERY_FAILED_TEXT = (
    "Не удалось передать вопрос Администратору. Пожалуйста, попробуйте ещё раз немного позже."
)


class FaqQuestion(StatesGroup):
    waiting_for_question = State()
    waiting_for_feedback = State()


async def begin_faq_dialog(message: Message, state: FSMContext) -> None:
    settings = get_settings()
    await state.set_state(FaqQuestion.waiting_for_question)
    await message.answer(
        "Напишите свой вопрос по Ascent Private одним сообщением.\n\n"
        "Мы дадим готовое решение или подготовим персональный ответ"
    )
    await send_faq_start_to_funnel(settings, message.from_user)


def _trim_answer(answer: str, limit: int = 1100) -> str:
    if len(answer) <= limit:
        return answer
    return answer[:limit].rstrip() + "..."


def _format_matches(matches: list[FaqMatch]) -> str:
    parts = ["Нашёл ответы, которые могут подойти по смыслу:\n"]
    for index, match in enumerate(matches, start=1):
        parts.append(
            f"<b>{index}. {escape(match.item.question)}</b>\n"
            f"{escape(_trim_answer(match.item.answer))}"
        )
    parts.append("Ваш вопрос решен?")
    return "\n\n".join(parts)


def _format_support_question(user: User | None, question: str) -> str:
    if user is None:
        user_block = "Пользователь: неизвестно"
    else:
        username = f"@{user.username}" if user.username else "-"
        full_name = " ".join(part for part in [user.first_name, user.last_name] if part) or "-"
        user_block = (
            f"Telegram ID: {user.id}\n"
            f"Username: {escape(username)}\n"
            f"Имя: {escape(full_name)}"
        )
    return (
        "<b>Новый вопрос из FAQ сайта</b>\n\n"
        f"{user_block}\n\n"
        f"<b>Вопрос:</b>\n{escape(question)}\n\n"
        "Чтобы ответить клиенту, отправьте ответ реплаем на это сообщение."
    )


def _extract_telegram_user_id(text: str) -> int | None:
    match = re.search(r"Telegram ID:\s*(\d+)", text)
    return int(match.group(1)) if match else None


@router.message(Command("faq"))
async def handle_faq_command(message: Message, state: FSMContext) -> None:
    await begin_faq_dialog(message, state)


@router.message(FaqQuestion.waiting_for_question, F.text)
async def handle_faq_question(message: Message, state: FSMContext) -> None:
    question = (message.text or "").strip()
    await state.update_data(question=question)
    settings = get_settings()
    await send_faq_question_to_funnel(settings, message.from_user, question)

    matches = find_faq_matches(question)
    if not matches:
        await state.clear()
        sent_to_support_chat = await notify_support_chat(
            settings,
            message.bot,
            _format_support_question(message.from_user, question),
        )
        await message.answer(
            FAQ_SUPPORT_QUEUED_TEXT if sent_to_support_chat else FAQ_SUPPORT_DELIVERY_FAILED_TEXT
        )
        return

    await state.set_state(FaqQuestion.waiting_for_feedback)
    await message.answer(_format_matches(matches), reply_markup=faq_helpful_keyboard())


@router.callback_query(FaqQuestion.waiting_for_feedback, F.data == FAQ_HELPFUL_YES)
async def handle_faq_helpful_yes(callback: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    await callback.answer()
    if callback.message:
        await callback.message.answer("Отлично. Рад, что ответ оказался полезен.")


@router.callback_query(FaqQuestion.waiting_for_feedback, F.data == FAQ_HELPFUL_NO)
async def handle_faq_helpful_no(callback: CallbackQuery, state: FSMContext) -> None:
    data = await state.get_data()
    question = str(data.get("question") or "").strip()
    await state.clear()
    await callback.answer()

    if question and callback.message:
        settings = get_settings()
        sent_to_support_chat = await notify_support_chat(
            settings,
            callback.message.bot,
            _format_support_question(callback.from_user, question),
        )
        await callback.message.answer(
            FAQ_SUPPORT_QUEUED_TEXT if sent_to_support_chat else FAQ_SUPPORT_DELIVERY_FAILED_TEXT
        )
    elif callback.message:
        await callback.message.answer(FAQ_SUPPORT_DELIVERY_FAILED_TEXT)


@router.message(F.chat.type == "private", F.text, ~F.text.startswith("/"))
async def handle_private_text_as_faq_question(message: Message, state: FSMContext) -> None:
    await handle_faq_question(message, state)


@router.message(F.reply_to_message, F.text)
async def handle_support_chat_reply(message: Message) -> None:
    settings = get_settings()
    if message.chat.id != settings.telegram_support_chat_id or message.from_user is None:
        return

    replied_text = message.reply_to_message.text if message.reply_to_message else ""
    telegram_user_id = _extract_telegram_user_id(replied_text or "")
    if telegram_user_id is None:
        return

    try:
        await message.bot.send_message(
            telegram_user_id,
            "Ответ администратора Ascent Private:\n\n" + escape(message.text or ""),
        )
        await message.reply("Ответ отправлен клиенту.")
    except Exception:
        logger.exception("Failed to send FAQ support reply to user %s", telegram_user_id)
        await message.reply("Не удалось отправить ответ клиенту.")
