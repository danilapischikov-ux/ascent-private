from aiogram import Dispatcher

from app.bot.handlers import admin, faq, payment, start, support


def create_dispatcher() -> Dispatcher:
    dispatcher = Dispatcher()
    dispatcher.include_router(start.router)
    dispatcher.include_router(faq.router)
    dispatcher.include_router(payment.router)
    dispatcher.include_router(support.router)
    dispatcher.include_router(admin.router)
    return dispatcher
