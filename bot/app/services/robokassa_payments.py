import json
from decimal import Decimal
from urllib.parse import quote, urlencode

from app.core.config import Settings
from app.db.models import Payment
from app.services.robokassa_signature import build_payment_signature, format_amount


def build_shp_params(payment: Payment) -> dict[str, str]:
    return {}


def build_receipt(settings: Settings, payment: Payment) -> str:
    receipt = {
        "items": [
            {
                "name": settings.robokassa_payment_description,
                "quantity": 1,
                "sum": format_amount(Decimal(payment.amount)),
                "tax": "none",
                "payment_method": "full_payment",
                "payment_object": "service",
            }
        ]
    }
    receipt_json = json.dumps(receipt, ensure_ascii=False, separators=(",", ":"))
    return quote(receipt_json, safe="")


def build_payment_payload(settings: Settings, payment: Payment) -> dict[str, str]:
    shp_params = build_shp_params(payment)
    receipt = build_receipt(settings, payment)
    signature = build_payment_signature(
        settings,
        out_sum=Decimal(payment.amount),
        inv_id=int(payment.inv_id),
        shp_params=shp_params,
        receipt=receipt,
    )
    payload = {
        "MerchantLogin": settings.robokassa_merchant_login,
        "OutSum": format_amount(Decimal(payment.amount)),
        "InvId": str(payment.inv_id),
        "Description": settings.robokassa_payment_description,
        "Receipt": receipt,
        "SignatureValue": signature,
        "ResultURL": settings.robokassa_result_url,
        "SuccessURL": settings.robokassa_success_url,
        "FailURL": settings.robokassa_fail_url,
        "Culture": "ru",
        "Encoding": "utf-8",
        "IsTest": "1" if settings.robokassa_is_test else "0",
        **shp_params,
    }
    payment.robokassa_signature = signature
    return payload


def build_payment_url(settings: Settings, payload: dict[str, str]) -> str:
    return f"{settings.robokassa_payment_url}?{urlencode(payload)}"
