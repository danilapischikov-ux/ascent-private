from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

FAQ_HELPFUL_YES = "faq_helpful_yes"
FAQ_HELPFUL_NO = "faq_helpful_no"


def url_keyboard(label: str, url: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text=label, url=url)]])


def payment_keyboard(url: str) -> InlineKeyboardMarkup:
    return url_keyboard("Оплатить", url)


def trial_keyboard(url: str) -> InlineKeyboardMarkup:
    return url_keyboard("Получить доступ", url)


def faq_helpful_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="Да", callback_data=FAQ_HELPFUL_YES),
                InlineKeyboardButton(text="Нет", callback_data=FAQ_HELPFUL_NO),
            ],
        ],
    )
