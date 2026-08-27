from aiogram.types import User as TelegramUser
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import User


async def get_by_telegram_id(session: AsyncSession, telegram_user_id: int) -> User | None:
    result = await session.execute(select(User).where(User.telegram_user_id == telegram_user_id))
    return result.scalar_one_or_none()


async def upsert_from_telegram(
    session: AsyncSession,
    telegram_user: TelegramUser,
    source: str | None = None,
) -> User:
    user = await get_by_telegram_id(session, telegram_user.id)
    if user is None:
        user = User(
            telegram_user_id=telegram_user.id,
            username=telegram_user.username,
            first_name=telegram_user.first_name,
            last_name=telegram_user.last_name,
            source=source,
        )
        session.add(user)
        await session.flush()
        return user

    user.username = telegram_user.username
    user.first_name = telegram_user.first_name
    user.last_name = telegram_user.last_name
    if source:
        user.source = source
    await session.flush()
    return user
