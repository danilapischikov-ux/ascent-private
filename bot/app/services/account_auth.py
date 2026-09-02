import asyncio
from datetime import timedelta

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import Settings
from app.core.security import (
    create_auth_token,
    create_temporary_password,
    hash_password,
    hash_secret,
    normalize_phone,
    utcnow,
    validate_password,
    verify_password,
)
from app.db.models import AccessEntitlement, AccountAuditEvent, WebAccount, WebSession
from app.services.email import send_email


GENERIC_EMAIL_RESPONSE = {"status": "ok", "message": "Если адрес доступен, письмо будет отправлено."}


def normalize_email(value: str) -> str:
    return value.strip().lower()


def _days_left(period_end) -> int | None:
    if period_end is None:
        return None
    return max(0, (period_end - utcnow()).days)


def build_auth_summary(account: WebAccount, entitlement: AccessEntitlement | None) -> dict:
    period_end = entitlement.current_period_end if entitlement else None
    return {
        "account": {"id": str(account.id), "name": account.name, "email": account.email, "phone": account.phone},
        "access": {
            "status": entitlement.access_status if entitlement else "email_pending",
            "current_period_end": period_end.isoformat() if period_end else None,
            "days_left": _days_left(period_end),
            "can_view_materials": False,
        },
        "security": {"must_change_password": account.must_change_password},
    }


async def record_audit(session: AsyncSession, account_id: int | None, event_type: str, payload: dict | None = None) -> None:
    session.add(AccountAuditEvent(account_id=account_id, event_type=event_type, payload=payload))
    await session.flush()


async def get_account_by_email(session: AsyncSession, email: str) -> WebAccount | None:
    result = await session.execute(select(WebAccount).where(WebAccount.email == normalize_email(email)))
    return result.scalar_one_or_none()


async def get_account_by_identifier(session: AsyncSession, identifier: str) -> WebAccount | None:
    normalized_email = normalize_email(identifier)
    if "@" in normalized_email:
        return await get_account_by_email(session, normalized_email)
    normalized_phone = normalize_phone(identifier)
    if normalized_phone is None:
        return None
    result = await session.execute(select(WebAccount).where(WebAccount.phone_normalized == normalized_phone))
    return result.scalar_one_or_none()


async def get_entitlement(session: AsyncSession, account_id: int) -> AccessEntitlement | None:
    result = await session.execute(select(AccessEntitlement).where(AccessEntitlement.account_id == account_id))
    return result.scalar_one_or_none()


async def register_account(
    session: AsyncSession,
    settings: Settings,
    *,
    name: str,
    email: str,
    phone: str,
) -> tuple[WebAccount, str]:
    normalized_phone = normalize_phone(phone)
    if normalized_phone is None:
        raise ValueError("Введите российский номер телефона в формате +7.")
    normalized_email = normalize_email(email)
    if await get_account_by_email(session, normalized_email):
        raise ValueError("Этот email уже зарегистрирован.")
    existing_phone = await get_account_by_identifier(session, normalized_phone)
    if existing_phone:
        raise ValueError("Этот номер телефона уже зарегистрирован.")

    now = utcnow()
    token = create_auth_token()
    account = WebAccount(
        name=name.strip(),
        email=normalized_email,
        phone=phone.strip(),
        phone_normalized=normalized_phone,
        email_verification_token_hash=hash_secret(token),
        email_verification_sent_at=now,
        email_verification_expires_at=now + timedelta(hours=settings.auth_confirmation_token_ttl_hours),
    )
    session.add(account)
    await session.flush()
    session.add(AccessEntitlement(account_id=account.id))
    await record_audit(session, account.id, "account_registered")
    await record_audit(session, account.id, "email_confirmation_sent")
    return account, token


async def confirm_email(session: AsyncSession, settings: Settings, token: str) -> tuple[WebAccount, str] | None:
    token_hash = hash_secret(token)
    result = await session.execute(
        select(WebAccount).where(WebAccount.email_verification_token_hash == token_hash).with_for_update()
    )
    account = result.scalar_one_or_none()
    if account is None or account.email_verification_expires_at is None or account.email_verification_expires_at <= utcnow():
        return None
    entitlement = await get_entitlement(session, account.id)
    if entitlement is None or account.email_verified_at is not None:
        return None

    now = utcnow()
    temporary_password = create_temporary_password()
    account.email_verified_at = now
    account.email_verification_token_hash = None
    account.email_verification_expires_at = None
    account.status = "active"
    account.password_hash = hash_password(temporary_password)
    account.temporary_password_sent_at = now
    account.must_change_password = True
    account.trial_used = True
    entitlement.access_status = "trial_active"
    entitlement.access_type = "trial"
    entitlement.trial_start_at = now
    entitlement.trial_end_at = now + timedelta(days=settings.trial_days)
    entitlement.current_period_end = entitlement.trial_end_at
    await record_audit(session, account.id, "email_confirmed")
    await record_audit(session, account.id, "temporary_password_created")
    await record_audit(session, account.id, "trial_activated")
    return account, temporary_password


async def resend_confirmation(session: AsyncSession, settings: Settings, email: str) -> tuple[WebAccount, str] | None:
    account = await get_account_by_email(session, email)
    if account is None or account.email_verified_at is not None or account.status != "email_pending":
        return None
    since = utcnow() - timedelta(hours=1)
    count_result = await session.execute(
        select(func.count(AccountAuditEvent.id)).where(
            AccountAuditEvent.account_id == account.id,
            AccountAuditEvent.event_type == "email_confirmation_sent",
            AccountAuditEvent.occurred_at >= since,
        )
    )
    if (count_result.scalar_one() or 0) >= 3:
        return None
    token = create_auth_token()
    now = utcnow()
    account.email_verification_token_hash = hash_secret(token)
    account.email_verification_sent_at = now
    account.email_verification_expires_at = now + timedelta(hours=settings.auth_confirmation_token_ttl_hours)
    await record_audit(session, account.id, "email_confirmation_sent")
    return account, token


async def authenticate(session: AsyncSession, identifier: str, password: str) -> tuple[WebAccount, AccessEntitlement] | None:
    if not password or len(password) > 256:
        return None
    account = await get_account_by_identifier(session, identifier)
    if account is None or account.status != "active" or account.email_verified_at is None or not account.password_hash:
        return None
    if not verify_password(password, account.password_hash):
        return None
    entitlement = await get_entitlement(session, account.id)
    if entitlement is None:
        return None
    account.last_login_at = utcnow()
    await record_audit(session, account.id, "login_success")
    return account, entitlement


async def create_session(
    session: AsyncSession,
    settings: Settings,
    account: WebAccount,
    *,
    user_agent: str | None,
    ip_address: str | None,
) -> str:
    token = create_auth_token()
    now = utcnow()
    session.add(
        WebSession(
            account_id=account.id,
            session_token_hash=hash_secret(token),
            expires_at=now + timedelta(days=settings.auth_session_ttl_days),
            last_seen_at=now,
            user_agent_hash=hash_secret(user_agent) if user_agent else None,
            ip_hash=hash_secret(ip_address) if ip_address else None,
        )
    )
    await record_audit(session, account.id, "session_created")
    return token


async def get_session_account(session: AsyncSession, token: str | None) -> tuple[WebAccount, AccessEntitlement, WebSession] | None:
    if not token:
        return None
    result = await session.execute(select(WebSession).where(WebSession.session_token_hash == hash_secret(token)))
    web_session = result.scalar_one_or_none()
    if web_session is None or web_session.revoked_at is not None or web_session.expires_at <= utcnow():
        return None
    account = await session.get(WebAccount, web_session.account_id)
    if account is None:
        return None
    entitlement = await get_entitlement(session, account.id)
    if entitlement is None:
        return None
    return account, entitlement, web_session


async def revoke_session(session: AsyncSession, web_session: WebSession, *, event_type: str = "logout") -> None:
    if web_session.revoked_at is None:
        web_session.revoked_at = utcnow()
        await record_audit(session, web_session.account_id, event_type)


async def revoke_all_sessions(session: AsyncSession, account_id: int, *, except_session_id: int | None = None) -> None:
    result = await session.execute(select(WebSession).where(WebSession.account_id == account_id, WebSession.revoked_at.is_(None)))
    for web_session in result.scalars():
        if web_session.id != except_session_id:
            web_session.revoked_at = utcnow()


async def change_password(session: AsyncSession, account: WebAccount, current_password: str, new_password: str, current_session: WebSession) -> bool:
    if not account.password_hash or not verify_password(current_password, account.password_hash) or not validate_password(new_password):
        return False
    account.password_hash = hash_password(new_password)
    account.must_change_password = False
    await revoke_all_sessions(session, account.id, except_session_id=current_session.id)
    await record_audit(session, account.id, "password_changed")
    return True


async def request_password_reset(session: AsyncSession, settings: Settings, email: str) -> tuple[WebAccount, str] | None:
    account = await get_account_by_email(session, email)
    if account is None or account.status != "active" or account.email_verified_at is None:
        return None
    since = utcnow() - timedelta(hours=1)
    count_result = await session.execute(
        select(func.count(AccountAuditEvent.id)).where(
            AccountAuditEvent.account_id == account.id,
            AccountAuditEvent.event_type == "password_reset_requested",
            AccountAuditEvent.occurred_at >= since,
        )
    )
    if (count_result.scalar_one() or 0) >= 5:
        return None
    token = create_auth_token()
    now = utcnow()
    account.password_reset_token_hash = hash_secret(token)
    account.password_reset_sent_at = now
    account.password_reset_expires_at = now + timedelta(hours=settings.auth_reset_token_ttl_hours)
    await record_audit(session, account.id, "password_reset_requested")
    return account, token


async def reset_password(session: AsyncSession, token: str, new_password: str) -> WebAccount | None:
    if not validate_password(new_password):
        return None
    result = await session.execute(
        select(WebAccount).where(WebAccount.password_reset_token_hash == hash_secret(token)).with_for_update()
    )
    account = result.scalar_one_or_none()
    if account is None or account.password_reset_expires_at is None or account.password_reset_expires_at <= utcnow():
        return None
    account.password_hash = hash_password(new_password)
    account.password_reset_token_hash = None
    account.password_reset_expires_at = None
    account.must_change_password = False
    await revoke_all_sessions(session, account.id)
    await record_audit(session, account.id, "password_reset_completed")
    return account


async def send_confirmation_email(settings: Settings, account: WebAccount, token: str) -> None:
    url = f"{settings.auth_public_api_url.rstrip('/')}/api/auth/confirm-email?token={token}"
    body = "\n".join(["Подтвердите email для Ascent Private.", "", f"Ссылка подтверждения: {url}", "", "Ссылка действует ограниченное время."])
    await asyncio.to_thread(send_email, settings, to_email=account.email, subject="Подтвердите email Ascent Private", body=body)


async def send_temporary_password_email(settings: Settings, account: WebAccount, password: str) -> None:
    body = "\n".join([
        "Ваш email подтверждён. Личный кабинет Ascent Private активирован.",
        "",
        "Для входа используйте email или телефон, указанные при регистрации.",
        f"Временный пароль: {password}",
        "",
        "Ознакомительный доступ активен на 30 дней. После входа смените временный пароль.",
        f"Войти: {settings.site_url}/account/login",
    ])
    await asyncio.to_thread(send_email, settings, to_email=account.email, subject="Доступ к Ascent Private", body=body)


async def send_password_reset_email(settings: Settings, account: WebAccount, token: str) -> None:
    url = f"{settings.site_url}/account/reset-password?token={token}"
    body = "\n".join(["Восстановление пароля Ascent Private.", "", f"Установить новый пароль: {url}", "", "Ссылка действует ограниченное время."])
    await asyncio.to_thread(send_email, settings, to_email=account.email, subject="Восстановление пароля Ascent Private", body=body)
