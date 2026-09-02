from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from fastapi.responses import RedirectResponse
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.schemas.auth import (
    ChangePasswordRequest,
    LoginRequest,
    RegisterRequest,
    RequestPasswordResetRequest,
    ResendConfirmationRequest,
    ResetPasswordRequest,
)
from app.core.config import Settings, get_settings
from app.db.session import get_db_session
from app.services import account_auth

router = APIRouter(prefix="/api/auth", tags=["auth"])


def _client_ip(request: Request) -> str | None:
    return request.client.host if request.client else None


def _require_allowed_origin(request: Request, settings: Settings) -> None:
    origin = request.headers.get("origin")
    if origin and origin not in settings.cors_origins:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Origin is not allowed")


def _set_session_cookie(response: Response, settings: Settings, token: str) -> None:
    response.set_cookie(
        key=settings.auth_session_cookie_name,
        value=token,
        max_age=settings.auth_session_ttl_days * 24 * 60 * 60,
        httponly=True,
        secure=settings.app_env.lower() == "production",
        samesite="lax",
        path="/",
    )


def _clear_session_cookie(response: Response, settings: Settings) -> None:
    response.delete_cookie(key=settings.auth_session_cookie_name, path="/")


async def _current_auth(
    request: Request,
    session: AsyncSession,
    settings: Settings,
):
    current = await account_auth.get_session_account(session, request.cookies.get(settings.auth_session_cookie_name))
    if current is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication is required")
    return current


@router.post("/register", status_code=status.HTTP_202_ACCEPTED)
async def register(
    payload: RegisterRequest,
    request: Request,
    session: AsyncSession = Depends(get_db_session),
) -> dict[str, str]:
    settings = get_settings()
    _require_allowed_origin(request, settings)
    if not (payload.consent_personal_data and payload.consent_offer and payload.consent_risk_disclaimer):
        raise HTTPException(status_code=422, detail="Required consents must be accepted")
    try:
        account, token = await account_auth.register_account(
            session, settings, name=payload.name, email=str(payload.email), phone=payload.phone
        )
        await session.commit()
    except (IntegrityError, ValueError) as error:
        await session.rollback()
        detail = str(error) if isinstance(error, ValueError) else "Этот email или номер телефона уже зарегистрирован."
        raise HTTPException(status_code=422, detail=detail) from error
    try:
        await account_auth.send_confirmation_email(settings, account, token)
    except Exception:
        await account_auth.record_audit(session, account.id, "email_confirmation_delivery_failed")
        await session.commit()
    return {"status": "email_confirmation_required", "message": "Письмо для подтверждения отправлено на email."}


@router.get("/confirm-email")
async def confirm_email(token: str, request: Request, session: AsyncSession = Depends(get_db_session)) -> RedirectResponse:
    settings = get_settings()
    confirmed = await account_auth.confirm_email(session, settings, token)
    if confirmed is None:
        await session.rollback()
        return RedirectResponse(f"{settings.site_url}/account/login?confirmation_expired=1", status_code=303)
    account, temporary_password = confirmed
    await session.commit()
    try:
        await account_auth.send_temporary_password_email(settings, account, temporary_password)
        await account_auth.record_audit(session, account.id, "temporary_password_sent")
    except Exception:
        await account_auth.record_audit(session, account.id, "temporary_password_delivery_failed")
    await session.commit()
    return RedirectResponse(f"{settings.site_url}/account/login?email_confirmed=1", status_code=303)


@router.post("/login")
async def login(
    payload: LoginRequest,
    request: Request,
    response: Response,
    session: AsyncSession = Depends(get_db_session),
) -> dict:
    settings = get_settings()
    _require_allowed_origin(request, settings)
    authenticated = await account_auth.authenticate(session, payload.identifier, payload.password.get_secret_value())
    if authenticated is None:
        await session.rollback()
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    account, entitlement = authenticated
    token = await account_auth.create_session(
        session, settings, account, user_agent=request.headers.get("user-agent"), ip_address=_client_ip(request)
    )
    await session.commit()
    _set_session_cookie(response, settings, token)
    return account_auth.build_auth_summary(account, entitlement)


@router.post("/change-password")
async def change_password(
    payload: ChangePasswordRequest,
    request: Request,
    session: AsyncSession = Depends(get_db_session),
) -> dict[str, bool]:
    settings = get_settings()
    _require_allowed_origin(request, settings)
    account, _entitlement, web_session = await _current_auth(request, session, settings)
    if not await account_auth.change_password(
        session,
        account,
        payload.current_password.get_secret_value(),
        payload.new_password.get_secret_value(),
        web_session,
    ):
        await session.rollback()
        raise HTTPException(status_code=422, detail="Current password or new password is invalid")
    await session.commit()
    return {"ok": True}


@router.post("/logout")
async def logout(request: Request, response: Response, session: AsyncSession = Depends(get_db_session)) -> dict[str, bool]:
    settings = get_settings()
    _require_allowed_origin(request, settings)
    current = await account_auth.get_session_account(session, request.cookies.get(settings.auth_session_cookie_name))
    if current is not None:
        _account, _entitlement, web_session = current
        await account_auth.revoke_session(session, web_session)
        await session.commit()
    _clear_session_cookie(response, settings)
    return {"ok": True}


@router.get("/me")
async def me(request: Request, session: AsyncSession = Depends(get_db_session)) -> dict:
    settings = get_settings()
    account, entitlement, _web_session = await _current_auth(request, session, settings)
    return account_auth.build_auth_summary(account, entitlement)


@router.post("/resend-confirmation", status_code=status.HTTP_202_ACCEPTED)
async def resend_confirmation(
    payload: ResendConfirmationRequest,
    request: Request,
    session: AsyncSession = Depends(get_db_session),
) -> dict[str, str]:
    settings = get_settings()
    _require_allowed_origin(request, settings)
    resend = await account_auth.resend_confirmation(session, settings, str(payload.email))
    await session.commit()
    if resend is not None:
        account, token = resend
        try:
            await account_auth.send_confirmation_email(settings, account, token)
        except Exception:
            await account_auth.record_audit(session, account.id, "email_confirmation_delivery_failed")
            await session.commit()
    return account_auth.GENERIC_EMAIL_RESPONSE


@router.post("/request-password-reset", status_code=status.HTTP_202_ACCEPTED)
async def request_password_reset(
    payload: RequestPasswordResetRequest,
    request: Request,
    session: AsyncSession = Depends(get_db_session),
) -> dict[str, str]:
    settings = get_settings()
    _require_allowed_origin(request, settings)
    reset = await account_auth.request_password_reset(session, settings, str(payload.email))
    await session.commit()
    if reset is not None:
        account, token = reset
        try:
            await account_auth.send_password_reset_email(settings, account, token)
        except Exception:
            await account_auth.record_audit(session, account.id, "password_reset_delivery_failed")
            await session.commit()
    return account_auth.GENERIC_EMAIL_RESPONSE


@router.post("/reset-password")
async def reset_password(
    payload: ResetPasswordRequest,
    request: Request,
    session: AsyncSession = Depends(get_db_session),
) -> dict[str, bool]:
    settings = get_settings()
    _require_allowed_origin(request, settings)
    account = await account_auth.reset_password(
        session,
        payload.token.get_secret_value(),
        payload.new_password.get_secret_value(),
    )
    if account is None:
        await session.rollback()
        raise HTTPException(status_code=422, detail="Reset token or password is invalid")
    await session.commit()
    return {"ok": True}
