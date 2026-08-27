from datetime import timedelta

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import Settings
from app.core.security import utcnow
from app.db.models import Payment, Subscription, User
from app.db.repositories import reminders as reminder_repo
from app.db.repositories import subscriptions as subscription_repo


async def activate_trial(session: AsyncSession, settings: Settings, user: User) -> Subscription:
    now = utcnow()
    user.trial_used = True
    subscription = await subscription_repo.create_subscription(
        session,
        user_id=user.id,
        type_="trial",
        start_date=now,
        end_date=now + timedelta(days=settings.trial_days),
    )
    await create_subscription_reminders(session, subscription)
    return subscription


async def activate_paid_subscription(
    session: AsyncSession,
    settings: Settings,
    user: User,
    payment: Payment,
) -> Subscription:
    now = utcnow()
    active_paid_subscription = await subscription_repo.get_active_paid_for_user(session, user.id)
    start_date = (
        active_paid_subscription.end_date
        if active_paid_subscription and active_paid_subscription.end_date > now
        else now
    )
    subscription = await subscription_repo.create_subscription(
        session,
        user_id=user.id,
        type_="paid",
        start_date=start_date,
        end_date=start_date + timedelta(days=max(settings.subscription_days - 1, 0)),
    )
    payment.activated_at = now
    await create_subscription_reminders(session, subscription)
    return subscription


async def create_subscription_reminders(session: AsyncSession, subscription: Subscription) -> None:
    for days_before in (3, 1):
        send_at = subscription.end_date - timedelta(days=days_before)
        if send_at > utcnow():
            await reminder_repo.create_reminder(
                session,
                user_id=subscription.user_id,
                subscription_id=subscription.id,
                type_=f"expires_in_{days_before}_days",
                send_at=send_at,
            )
