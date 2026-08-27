from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import ChannelAccess


async def create_access(
    session: AsyncSession,
    *,
    user_id: int,
    subscription_id: int,
    invite_link: str | None,
    expires_at,
) -> ChannelAccess:
    access = ChannelAccess(
        user_id=user_id,
        subscription_id=subscription_id,
        invite_link=invite_link,
        expires_at=expires_at,
        status="active",
    )
    session.add(access)
    await session.flush()
    return access


async def get_active_for_subscription(session: AsyncSession, subscription_id: int) -> ChannelAccess | None:
    result = await session.execute(
        select(ChannelAccess).where(
            ChannelAccess.subscription_id == subscription_id,
            ChannelAccess.status == "active",
        ),
    )
    return result.scalar_one_or_none()
