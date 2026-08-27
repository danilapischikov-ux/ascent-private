from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Subscription


async def get_active_for_user(session: AsyncSession, user_id: int) -> Subscription | None:
    result = await session.execute(
        select(Subscription)
        .where(Subscription.user_id == user_id, Subscription.status == "active")
        .order_by(Subscription.end_date.desc())
        .limit(1),
    )
    return result.scalar_one_or_none()


async def get_active_paid_for_user(session: AsyncSession, user_id: int) -> Subscription | None:
    result = await session.execute(
        select(Subscription)
        .where(
            Subscription.user_id == user_id,
            Subscription.status == "active",
            Subscription.type == "paid",
        )
        .order_by(Subscription.end_date.desc())
        .limit(1),
    )
    return result.scalar_one_or_none()


async def list_expired_active(session: AsyncSession, now: datetime) -> list[Subscription]:
    result = await session.execute(
        select(Subscription).where(Subscription.status == "active", Subscription.end_date <= now),
    )
    return list(result.scalars().all())


async def create_subscription(
    session: AsyncSession,
    *,
    user_id: int,
    type_: str,
    start_date: datetime,
    end_date: datetime,
) -> Subscription:
    subscription = Subscription(
        user_id=user_id,
        type=type_,
        status="active",
        start_date=start_date,
        end_date=end_date,
    )
    session.add(subscription)
    await session.flush()
    return subscription
