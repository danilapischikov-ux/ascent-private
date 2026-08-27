from pydantic import BaseModel, EmailStr, Field

from app.api.schemas.events import EventAttribution


class CreateRobokassaPaymentRequest(BaseModel):
    payment_token: str = Field(min_length=16, max_length=160)
    customer_name: str = Field(min_length=1, max_length=255)
    customer_email: EmailStr
    customer_phone: str = Field(min_length=5, max_length=64)
    lead_id: str | None = Field(default=None, max_length=128)
    session_id: str | None = Field(default=None, max_length=128)
    client_id: str | None = Field(default=None, max_length=128)
    yclid: str | None = Field(default=None, max_length=128)
    attribution: EventAttribution | None = None


class CreateRobokassaPaymentResponse(BaseModel):
    payment_url: str
    robokassa_payload: dict[str, str]
    telegram_user_id: int


class CreateYooKassaPaymentRequest(CreateRobokassaPaymentRequest):
    pass


class CreateYooKassaPaymentResponse(BaseModel):
    provider: str
    payment_id: int
    payment_token: str
    payment_url: str
    provider_payment_id: str
    telegram_user_id: int
