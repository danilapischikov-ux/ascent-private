from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Reminder


async def create_reminder(
    session: AsyncSession,
    *,
    user_id: int,
    subscription_id: int,
    type_: str,
    send_at: datetime,
) -> Reminder:
    reminder = Reminder(
        user_id=user_id,
        subscription_id=subscription_id,
        type=type_,
        send_at=send_at,
        status="pending",
    )
    session.add(reminder)
    await session.flush()
    return reminder


async def list_due(session: AsyncSession, now: datetime) -> list[Reminder]:
    result = await session.execute(
        select(Reminder).where(Reminder.status == "pending", Reminder.send_at <= now),
    )
    return list(result.scalars().all())
