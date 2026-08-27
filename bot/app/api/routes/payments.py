from decimal import Decimal
from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.schemas.payments import (
    CreateRobokassaPaymentRequest,
    CreateRobokassaPaymentResponse,
    CreateYooKassaPaymentRequest,
    CreateYooKassaPaymentResponse,
)
from app.core.config import get_settings
from app.core.security import utcnow
from app.db.repositories import analytics as analytics_repo
from app.db.repositories import payments as payment_repo
from app.db.session import get_db_session
from app.services.robokassa_payments import build_payment_payload, build_payment_url
from app.services.yookassa_payments import YooKassaApiError, create_yookassa_payment

router = APIRouter(prefix="/api/payments", tags=["payments"])


@router.post("/robokassa/create", response_model=CreateRobokassaPaymentResponse)
async def create_robokassa_payment(
    payload: CreateRobokassaPaymentRequest,
    session: AsyncSession = Depends(get_db_session),
) -> CreateRobokassaPaymentResponse:
    settings = get_settings()
    if settings.payment_provider != "ROBOKASSA":
        raise HTTPException(status_code=503, detail="Robokassa payments are not active")

    payment = await payment_repo.get_by_token(session, payload.payment_token)
    if payment is None:
        raise HTTPException(status_code=404, detail="Payment token not found")
    if payment.created_at and payment.created_at + timedelta(minutes=settings.payment_token_ttl_minutes) < utcnow():
        raise HTTPException(status_code=410, detail="Payment token expired")
    if payment.status == "paid":
        raise HTTPException(status_code=409, detail="Payment is already paid")
    if Decimal(payment.amount) != Decimal(settings.subscription_rub_price):
        raise HTTPException(status_code=409, detail="Unexpected payment amount")

    attribution = payload.attribution.model_dump(exclude_none=True) if payload.attribution else None
    yclid = payload.yclid or (attribution or {}).get("yclid")
    await payment_repo.attach_customer_data(
        session,
        payment,
        name=payload.customer_name.strip(),
        email=str(payload.customer_email).strip(),
        phone=payload.customer_phone.strip(),
        lead_id=payload.lead_id.strip() if payload.lead_id else None,
        session_id=payload.session_id.strip() if payload.session_id else None,
        client_id=payload.client_id.strip() if payload.client_id else None,
        yclid=yclid.strip() if yclid else None,
        attribution=attribution,
    )
    await analytics_repo.upsert_lead_attribution(
        session,
        lead_id=payment.lead_id,
        session_id=payment.session_id,
        client_id=payment.client_id,
        yclid=payment.yclid,
        payment_token=payment.payment_token,
        payment_id=payment.id,
        telegram_user_id=payment.telegram_user_id,
        attribution=payment.attribution,
    )
    robokassa_payload = build_payment_payload(settings, payment)
    await session.commit()
    return CreateRobokassaPaymentResponse(
        payment_url=build_payment_url(settings, robokassa_payload),
        robokassa_payload=robokassa_payload,
        telegram_user_id=payment.telegram_user_id,
    )


@router.post("/yookassa/create", response_model=CreateYooKassaPaymentResponse)
async def create_yookassa_payment_route(
    payload: CreateYooKassaPaymentRequest,
    session: AsyncSession = Depends(get_db_session),
) -> CreateYooKassaPaymentResponse:
    settings = get_settings()
    if settings.payment_provider != "YOOKASSA":
        raise HTTPException(status_code=503, detail="YooKassa payments are not active")

    payment = await payment_repo.get_by_token(session, payload.payment_token)
    if payment is None:
        raise HTTPException(status_code=404, detail="Payment token not found")
    if payment.created_at and payment.created_at + timedelta(minutes=settings.payment_token_ttl_minutes) < utcnow():
        raise HTTPException(status_code=410, detail="Payment token expired")
    if payment.status == "paid":
        raise HTTPException(status_code=409, detail="Payment is already paid")
    if Decimal(payment.amount) != Decimal(settings.subscription_rub_price):
        raise HTTPException(status_code=409, detail="Unexpected payment amount")
    if payment.provider == "yookassa" and payment.provider_payment_id and payment.provider_confirmation_url:
        return CreateYooKassaPaymentResponse(
            provider="yookassa",
            payment_id=payment.id,
            payment_token=payment.payment_token,
            payment_url=payment.provider_confirmation_url,
            provider_payment_id=payment.provider_payment_id,
            telegram_user_id=payment.telegram_user_id,
        )

    attribution = payload.attribution.model_dump(exclude_none=True) if payload.attribution else None
    yclid = payload.yclid or (attribution or {}).get("yclid")
    await payment_repo.attach_customer_data(
        session,
        payment,
        name=payload.customer_name.strip(),
        email=str(payload.customer_email).strip(),
        phone=payload.customer_phone.strip(),
        lead_id=payload.lead_id.strip() if payload.lead_id else None,
        session_id=payload.session_id.strip() if payload.session_id else None,
        client_id=payload.client_id.strip() if payload.client_id else None,
        yclid=yclid.strip() if yclid else None,
        attribution=attribution,
    )
    await analytics_repo.upsert_lead_attribution(
        session,
        lead_id=payment.lead_id,
        session_id=payment.session_id,
        client_id=payment.client_id,
        yclid=payment.yclid,
        payment_token=payment.payment_token,
        payment_id=payment.id,
        telegram_user_id=payment.telegram_user_id,
        attribution=payment.attribution,
    )

    try:
        result = await create_yookassa_payment(settings, payment)
    except YooKassaApiError as error:
        raise HTTPException(status_code=502, detail="Unable to create YooKassa payment") from error

    if not result.confirmation_url:
        raise HTTPException(status_code=502, detail="YooKassa payment does not contain a confirmation URL")

    await payment_repo.attach_provider_payment(
        session,
        payment,
        provider="yookassa",
        provider_payment_id=result.provider_payment_id,
        provider_status=result.status,
        provider_confirmation_url=result.confirmation_url,
        provider_created_payload=result.payload,
    )
    await session.commit()
    return CreateYooKassaPaymentResponse(
        provider="yookassa",
        payment_id=payment.id,
        payment_token=payment.payment_token,
        payment_url=result.confirmation_url,
        provider_payment_id=result.provider_payment_id,
        telegram_user_id=payment.telegram_user_id,
    )
