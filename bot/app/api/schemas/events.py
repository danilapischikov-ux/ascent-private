from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, model_validator


class EventAttribution(BaseModel):
    model_config = ConfigDict(extra="allow")

    utm_source: str | None = Field(default=None, max_length=128)
    utm_medium: str | None = Field(default=None, max_length=128)
    utm_campaign: str | None = Field(default=None, max_length=255)
    utm_content: str | None = Field(default=None, max_length=255)
    utm_term: str | None = Field(default=None, max_length=255)
    yclid: str | None = Field(default=None, max_length=128)
    raw: dict[str, Any] | None = None


class SiteEventRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    event_id: str | None = Field(default=None, max_length=128)
    event_type: str | None = Field(default=None, min_length=1, max_length=64)
    event_name: str | None = Field(default=None, min_length=1, max_length=64)
    occurred_at: datetime | None = None
    lead_id: str | None = Field(default=None, max_length=128)
    session_id: str | None = Field(default=None, max_length=128)
    client_id: str | None = Field(default=None, max_length=128)
    yclid: str | None = Field(default=None, max_length=128)
    payment_token: str | None = Field(default=None, max_length=128)
    telegram_user_id: int | None = None
    url: str | None = None
    page_url: str | None = None
    referrer: str | None = None
    page: dict[str, Any] | None = None
    params: dict[str, Any] | None = None
    attribution: EventAttribution | None = None
    payload: dict[str, Any] | None = None

    @model_validator(mode="after")
    def normalize_frontend_payload(self) -> "SiteEventRequest":
        if self.event_type is None:
            self.event_type = self.event_name
        if self.event_type is None:
            raise ValueError("event_type or event_name is required")
        if self.url is None:
            self.url = self.page_url
        if self.url is None and self.page:
            value = self.page.get("url")
            self.url = str(value) if value is not None else None
        if self.referrer is None and self.page:
            value = self.page.get("referrer")
            self.referrer = str(value) if value is not None else None
        if self.payload is None:
            self.payload = {}
        if self.params is not None:
            self.payload["params"] = self.params
        if self.page is not None:
            self.payload["page"] = self.page
        return self


class SiteEventResponse(BaseModel):
    event_id: str | None
    stored: bool
