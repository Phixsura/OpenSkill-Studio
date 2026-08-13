from datetime import datetime

from pydantic import BaseModel, EmailStr, field_validator

from app.core.passwords import is_common_password


def _validate_password_strength(v: str) -> str:
    """Shared password strength rules (OWASP)."""
    if len(v) < 8:
        raise ValueError("Password must be at least 8 characters")
    if len(v) > 128:
        raise ValueError("Password must not exceed 128 characters")
    if not any(c.isupper() for c in v):
        raise ValueError("Password must contain at least one uppercase letter")
    if not any(c.isdigit() for c in v):
        raise ValueError("Password must contain at least one digit")
    if is_common_password(v):
        raise ValueError("This password is too common")
    return v


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    display_name: str

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        return _validate_password_strength(v)

    @field_validator("display_name")
    @classmethod
    def validate_display_name(cls, v: str) -> str:
        v = v.strip()
        if len(v) < 2:
            raise ValueError("Display name must be at least 2 characters")
        if len(v) > 100:
            raise ValueError("Display name must not exceed 100 characters")
        return v


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class ChangePasswordRequest(BaseModel):
    old_password: str
    new_password: str

    @field_validator("new_password")
    @classmethod
    def validate_new_password(cls, v: str) -> str:
        return _validate_password_strength(v)


class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str

    @field_validator("new_password")
    @classmethod
    def validate_new_password(cls, v: str) -> str:
        return _validate_password_strength(v)


class SessionResponse(BaseModel):
    id: str
    device_info: str | None
    ip_address: str | None
    created_at: datetime
    expires_at: datetime

    model_config = {"from_attributes": True}
