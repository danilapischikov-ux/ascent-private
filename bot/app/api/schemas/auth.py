from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.api.schemas.events import EventAttribution


class RegisterRequest(BaseModel):
    # Registration deliberately has no password.  Reject unknown fields rather
    # than silently accepting one, so a client cannot assume it was stored.
    model_config = ConfigDict(extra="forbid")

    name: str = Field(min_length=1, max_length=255)
    email: EmailStr
    phone: str = Field(min_length=5, max_length=64)
    consent_personal_data: bool
    consent_offer: bool
    consent_risk_disclaimer: bool
    attribution: EventAttribution | None = None


class LoginRequest(BaseModel):
    identifier: str = Field(min_length=1, max_length=255)
    password: str = Field(min_length=1, max_length=256)


class ChangePasswordRequest(BaseModel):
    current_password: str = Field(min_length=1, max_length=256)
    new_password: str = Field(min_length=12, max_length=256)


class ResendConfirmationRequest(BaseModel):
    email: EmailStr


class RequestPasswordResetRequest(BaseModel):
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    token: str = Field(min_length=16, max_length=256)
    new_password: str = Field(min_length=12, max_length=256)
