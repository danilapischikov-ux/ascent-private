from __future__ import annotations

import csv
from dataclasses import dataclass
from io import StringIO
from typing import Any

import httpx

from app.core.config import Settings


@dataclass(frozen=True)
class DirectReportResult:
    status_code: int
    request_id: str | None
    retry_in: int | None
    units: str | None
    rows: list[dict[str, str]]
    raw_tsv: str


class YandexDirectAdapter:
    """Read-only Yandex Direct Reports adapter.

    Write methods intentionally do not live here. Limited write must go through
    the safety validator and a separate executor after dry-run/rollback QA.
    """

    def __init__(self, settings: Settings, client: httpx.AsyncClient | None = None) -> None:
        self.settings = settings
        self.client = client or httpx.AsyncClient(timeout=90)

    def _headers(self) -> dict[str, str]:
        headers = {
            "Authorization": f"Bearer {self.settings.yandex_direct_oauth_token}",
            "Accept-Language": "ru",
            "processingMode": "auto",
            "returnMoneyInMicros": "false",
            "skipReportHeader": "true",
            "skipColumnHeader": "false",
            "skipReportSummary": "true",
        }
        if self.settings.yandex_direct_client_login:
            headers["Client-Login"] = self.settings.yandex_direct_client_login
        if self.settings.yandex_direct_use_operator_units:
            headers["Use-Operator-Units"] = "true"
        return headers

    async def fetch_report(self, body: dict[str, Any]) -> DirectReportResult:
        response = await self.client.post(
            self.settings.yandex_direct_reports_api_url,
            headers=self._headers(),
            json=body,
        )
        retry_in_header = response.headers.get("retryIn") or response.headers.get("Retry-In")
        retry_in = int(retry_in_header) if retry_in_header and retry_in_header.isdigit() else None
        raw_tsv = response.text if response.status_code == 200 else ""
        return DirectReportResult(
            status_code=response.status_code,
            request_id=response.headers.get("RequestId"),
            retry_in=retry_in,
            units=response.headers.get("Units") or response.headers.get("Units-Used-Login"),
            rows=parse_direct_report_tsv(raw_tsv) if raw_tsv else [],
            raw_tsv=raw_tsv,
        )


def parse_direct_report_tsv(raw_tsv: str) -> list[dict[str, str]]:
    if not raw_tsv.strip():
        return []
    reader = csv.DictReader(StringIO(raw_tsv), delimiter="\t")
    return [dict(row) for row in reader]
