from __future__ import annotations

import csv
from dataclasses import dataclass
from datetime import datetime
from io import StringIO

import httpx

from app.core.config import Settings


@dataclass(frozen=True)
class OfflineConversion:
    identifier: str
    target: str
    occurred_at: datetime
    price: str | None = None
    currency: str | None = None


class YandexMetrikaAdapter:
    def __init__(self, settings: Settings, client: httpx.AsyncClient | None = None) -> None:
        self.settings = settings
        self.client = client or httpx.AsyncClient(timeout=90)

    def _headers(self) -> dict[str, str]:
        return {"Authorization": f"OAuth {self.settings.yandex_metrika_oauth_token}"}

    async def upload_offline_conversions(self, conversions: list[OfflineConversion]) -> httpx.Response:
        counter_id = self.settings.yandex_metrika_counter_id
        id_type = self.settings.yandex_metrika_offline_conversion_id_type
        csv_body = build_offline_conversions_csv(conversions, identifier_column=id_type)
        url = (
            f"{self.settings.yandex_metrika_api_base_url}"
            f"/management/v1/counter/{counter_id}/offline_conversions/upload"
        )
        files = {"file": ("offline_conversions.csv", csv_body.encode("utf-8"), "text/csv")}
        return await self.client.post(url, headers=self._headers(), files=files)


def build_offline_conversions_csv(
    conversions: list[OfflineConversion],
    *,
    identifier_column: str = "CLIENT_ID",
) -> str:
    normalized_identifier = "ClientID" if identifier_column == "CLIENT_ID" else "yclid"
    output = StringIO()
    writer = csv.DictWriter(
        output,
        fieldnames=[normalized_identifier, "Target", "DateTime", "Price", "Currency"],
    )
    writer.writeheader()
    for conversion in conversions:
        writer.writerow(
            {
                normalized_identifier: conversion.identifier,
                "Target": conversion.target,
                "DateTime": conversion.occurred_at.strftime("%Y-%m-%d %H:%M:%S"),
                "Price": conversion.price or "",
                "Currency": conversion.currency or "",
            }
        )
    return output.getvalue()
