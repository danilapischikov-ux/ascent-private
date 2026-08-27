from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_UP
from typing import Any

import httpx

from app.core.config import Settings
from app.db.models import Payment


class YooKassaApiError(RuntimeError):
    """Raised when YooKassa credentials, transport, or response data are invalid."""


@dataclass(frozen=True)
class YooKassaPaymentResult:
    provider_payment_id: str
    status: str
    amount: str
    currency: str
    metadata: dict[str, Any]
    confirmation_url: str | None
    payload: dict[str, Any]


def format_amount(amount: Decimal) -> str:
    return str(amount.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))


def build_idempotence_key(payment: Payment) -> str:
    return f"ascent-private-payment-{payment.id}"


def build_create_payload(settings: Settings, payment: Payment) -> dict[str, Any]:
    if not payment.customer_email and not payment.customer_phone:
        raise YooKassaApiError("YooKassa receipt requires a customer email or phone")

    payload: dict[str, Any] = {
        "amount": {
            "value": format_amount(payment.amount),
            "currency": payment.currency,
        },
        "capture": settings.yookassa_capture,
        "confirmation": {
            "type": "redirect",
            "return_url": settings.yookassa_return_url,
        },
        "description": settings.yookassa_payment_description,
        "metadata": {
            "payment_id": str(payment.id),
            "payment_token": payment.payment_token,
            "telegram_user_id": str(payment.telegram_user_id),
        },
    }

    if settings.yookassa_receipt_enabled:
        customer: dict[str, str] = {}
        if payment.customer_email:
            customer["email"] = payment.customer_email
        elif payment.customer_phone:
            customer["phone"] = payment.customer_phone

        payload["receipt"] = {
            "customer": customer,
            "items": [
                {
                    "description": settings.yookassa_payment_description,
                    "quantity": "1.00",
                    "amount": {
                        "value": format_amount(payment.amount),
                        "currency": payment.currency,
                    },
                    "vat_code": settings.yookassa_vat_code,
                    "payment_mode": settings.yookassa_payment_mode,
                    "payment_subject": settings.yookassa_payment_subject,
                }
            ],
        }

    return payload


def _api_url(settings: Settings, path: str) -> str:
    return f"{str(settings.yookassa_api_url).rstrip('/')}{path}"


def _auth(settings: Settings) -> tuple[str, str]:
    if not settings.yookassa_shop_id or not settings.yookassa_secret_key:
        raise YooKassaApiError("YooKassa credentials are not configured")
    return settings.yookassa_shop_id, settings.yookassa_secret_key


def parse_payment_result(payload: dict[str, Any]) -> YooKassaPaymentResult:
    provider_payment_id = payload.get("id")
    status = payload.get("status")
    amount = payload.get("amount")
    metadata = payload.get("metadata") or {}
    confirmation = payload.get("confirmation") or {}

    if not isinstance(provider_payment_id, str) or not isinstance(status, str):
        raise YooKassaApiError("YooKassa response does not contain a payment id and status")
    if not isinstance(amount, dict) or not isinstance(amount.get("value"), str) or not isinstance(amount.get("currency"), str):
        raise YooKassaApiError("YooKassa response does not contain a valid amount")
    if not isinstance(metadata, dict) or not isinstance(confirmation, dict):
        raise YooKassaApiError("YooKassa response contains invalid metadata or confirmation")

    confirmation_url = confirmation.get("confirmation_url")
    if confirmation_url is not None and not isinstance(confirmation_url, str):
        raise YooKassaApiError("YooKassa response contains an invalid confirmation URL")

    return YooKassaPaymentResult(
        provider_payment_id=provider_payment_id,
        status=status,
        amount=amount["value"],
        currency=amount["currency"],
        metadata=metadata,
        confirmation_url=confirmation_url,
        payload=payload,
    )


async def create_yookassa_payment(settings: Settings, payment: Payment) -> YooKassaPaymentResult:
    payload = build_create_payload(settings, payment)
    try:
        async with httpx.AsyncClient(timeout=30, auth=_auth(settings)) as client:
            response = await client.post(
                _api_url(settings, "/payments"),
                headers={"Idempotence-Key": build_idempotence_key(payment)},
                json=payload,
            )
            response.raise_for_status()
            response_payload = response.json()
    except httpx.HTTPError as error:
        raise YooKassaApiError("YooKassa create payment request failed") from error

    if not isinstance(response_payload, dict):
        raise YooKassaApiError("YooKassa create payment response must be an object")
    return parse_payment_result(response_payload)


async def get_yookassa_payment(settings: Settings, provider_payment_id: str) -> YooKassaPaymentResult:
    if not provider_payment_id:
        raise YooKassaApiError("YooKassa payment id is required")

    try:
        async with httpx.AsyncClient(timeout=30, auth=_auth(settings)) as client:
            response = await client.get(_api_url(settings, f"/payments/{provider_payment_id}"))
            response.raise_for_status()
            response_payload = response.json()
    except httpx.HTTPError as error:
        raise YooKassaApiError("YooKassa get payment request failed") from error

    if not isinstance(response_payload, dict):
        raise YooKassaApiError("YooKassa get payment response must be an object")
    return parse_payment_result(response_payload)
