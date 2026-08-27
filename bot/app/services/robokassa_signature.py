import hashlib
from decimal import Decimal

from app.core.config import Settings
from app.core.security import constant_time_equal


def format_amount(amount: Decimal) -> str:
    return f"{amount:.2f}"


def _hash(value: str, algorithm: str) -> str:
    if algorithm == "SHA256":
        return hashlib.sha256(value.encode("utf-8")).hexdigest()
    return hashlib.md5(value.encode("utf-8")).hexdigest()


def _shp_tail(shp_params: dict[str, str]) -> str:
    if not shp_params:
        return ""
    parts = [f"{key}={shp_params[key]}" for key in sorted(shp_params)]
    return ":" + ":".join(parts)


def build_payment_signature(
    settings: Settings,
    *,
    out_sum: Decimal,
    inv_id: int,
    shp_params: dict[str, str],
    receipt: str | None = None,
) -> str:
    receipt_part = f"{receipt}:" if receipt else ""
    base = (
        f"{settings.robokassa_merchant_login}:"
        f"{format_amount(out_sum)}:"
        f"{inv_id}:"
        f"{receipt_part}"
        f"{settings.robokassa_password_for_payment}"
        f"{_shp_tail(shp_params)}"
    )
    return _hash(base, settings.robokassa_hash_algorithm)


def build_result_signature(
    settings: Settings,
    *,
    out_sum: Decimal | str,
    inv_id: int,
    shp_params: dict[str, str],
) -> str:
    out_sum_text = str(out_sum) if isinstance(out_sum, str) else format_amount(out_sum)
    base = (
        f"{out_sum_text}:"
        f"{inv_id}:"
        f"{settings.robokassa_password_for_result}"
        f"{_shp_tail(shp_params)}"
    )
    return _hash(base, settings.robokassa_hash_algorithm)


def verify_result_signature(
    settings: Settings,
    *,
    out_sum: Decimal | str,
    inv_id: int,
    shp_params: dict[str, str],
    signature: str,
) -> bool:
    expected = build_result_signature(
        settings,
        out_sum=out_sum,
        inv_id=inv_id,
        shp_params=shp_params,
    )
    return constant_time_equal(expected, signature)
