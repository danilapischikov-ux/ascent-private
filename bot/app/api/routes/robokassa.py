from decimal import Decimal, InvalidOperation
import logging

from aiogram import Bot
from fastapi import APIRouter, Depends, HTTPException, Request, Response
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.db.models import User
from app.db.repositories import analytics as analytics_repo
from app.db.repositories import payments as payment_repo
from app.db.session import get_db_session
from app.services.admin_reports import send_payment_reports_once
from app.services.channel_access import issue_channel_access
from app.services.robokassa_signature import verify_result_signature
from app.services.subscriptions import activate_paid_subscription

router = APIRouter(tags=["robokassa"])
logger = logging.getLogger(__name__)


async def _collect_params(request: Request) -> dict[str, str]:
    if request.method == "POST":
        form = await request.form()
        return {key: str(value) for key, value in form.items()}
    return {key: value for key, value in request.query_params.items()}


async def handle_result(request: Request, session: AsyncSession) -> str:
    settings = get_settings()
    params = await _collect_params(request)
    try:
        out_sum_text = params["OutSum"]
        inv_id = int(params["InvId"])
        out_sum = Decimal(out_sum_text)
        signature = params["SignatureValue"]
    except (KeyError, ValueError, InvalidOperation) as exc:
        logger.warning("Invalid Robokassa payload keys=%s", sorted(params.keys()))
        raise HTTPException(status_code=400, detail="Invalid Robokassa payload") from exc

    shp_params = {key: value for key, value in params.items() if key.startswith("Shp_")}
    if not verify_result_signature(
        settings,
        out_sum=out_sum_text,
        inv_id=inv_id,
        shp_params=shp_params,
        signature=signature,
    ):
        logger.warning(
            "Invalid Robokassa signature inv_id=%s out_sum=%s shp_keys=%s",
            inv_id,
            out_sum_text,
            sorted(shp_params.keys()),
        )
        raise HTTPException(status_code=400, detail="Invalid Robokassa signature")

    payment = await payment_repo.get_by_inv_id_for_update(session, inv_id)
    if payment is None:
        logger.warning("Robokassa payment not found inv_id=%s", inv_id)
        raise HTTPException(status_code=404, detail="Payment not found")
    if Decimal(payment.amount) != out_sum:
        logger.warning("Unexpected Robokassa amount inv_id=%s expected=%s actual=%s", inv_id, payment.amount, out_sum)
        raise HTTPException(status_code=409, detail="Unexpected amount")
    if shp_params.get("Shp_payment_id") not in (None, str(payment.id)):
        logger.warning("Unexpected Robokassa payment id inv_id=%s", inv_id)
        raise HTTPException(status_code=409, detail="Unexpected payment id")
    if shp_params.get("Shp_payment_token") not in (None, payment.payment_token):
        logger.warning("Unexpected Robokassa payment token inv_id=%s", inv_id)
        raise HTTPException(status_code=409, detail="Unexpected payment token")
    if shp_params.get("Shp_telegram_user_id") not in (None, str(payment.telegram_user_id)):
        logger.warning("Unexpected Robokassa Telegram user inv_id=%s", inv_id)
        raise HTTPException(status_code=409, detail="Unexpected Telegram user")

    changed = await payment_repo.mark_paid_once(session, payment, raw_result=params)
    await analytics_repo.record_payment_confirmed(session, payment, params)
    if changed or payment.activated_at is None:
        user = await session.get(User, payment.user_id)
        if user is None:
            raise HTTPException(status_code=404, detail="User not found")
        subscription = await activate_paid_subscription(session, settings, user, payment)
        bot: Bot = request.app.state.bot
        await issue_channel_access(session, settings, bot, user=user, subscription=subscription)
        await send_payment_reports_once(session, settings, bot, payment=payment, user=user, subscription=subscription)
    await session.commit()
    return f"OK{inv_id}"


@router.api_route("/robokassa/result", methods=["GET", "POST"])
async def robokassa_result(
    request: Request,
    session: AsyncSession = Depends(get_db_session),
) -> Response:
    result = await handle_result(request, session)
    return Response(content=result, media_type="text/plain")


@router.api_route("/robokassa/success", methods=["GET", "POST"])
async def robokassa_success() -> RedirectResponse:
    settings = get_settings()
    return RedirectResponse(settings.payment_success_url, status_code=303)


@router.api_route("/robokassa/fail", methods=["GET", "POST"])
async def robokassa_fail() -> RedirectResponse:
    settings = get_settings()
    return RedirectResponse(settings.payment_fail_url, status_code=303)
