import re
from datetime import datetime

from pydantic import BaseModel, field_validator


class UserResponse(BaseModel):
    id: str
    email: str
    email_verified: bool
    display_name: str
    avatar_url: str | None
    role: str
    created_at: datetime

    model_config = {"from_attributes": True}


class AuthResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user: UserResponse


class UpdateProfileRequest(BaseModel):
    display_name: str | None = None
    avatar_url: str | None = None

    @field_validator("display_name")
    @classmethod
    def validate_display_name(cls, v: str | None) -> str | None:
        if v is None:
            return v
        # Same rules as registration — update must not allow a blank name
        # (it renders empty in member lists and comment threads).
        v = v.strip()
        if len(v) < 2:
            raise ValueError("Display name must be at least 2 characters")
        if len(v) > 100:
            raise ValueError("Display Name must not exceed 100 characters")
        return v

    @field_validator("avatar_url")
    @classmethod
    def validate_avatar_url(cls, v: str | None) -> str | None:
        if v is None:
            return v
        if len(v) > 500:
            raise ValueError("Avatar Url must not exceed 500 characters")
        # Rendered as <img src> — javascript:/data: would be stored XSS.
        if v and not re.match(r"^https?://", v, re.IGNORECASE):
            raise ValueError("Avatar URL must start with http:// or https://")
        return v


class AdminUpdateRoleRequest(BaseModel):
    role: str


class AdminUserResponse(UserResponse):
    """Extended user response for admin views."""

    status: str
    last_login_at: datetime | None
    updated_at: datetime

    model_config = {"from_attributes": True}
