from datetime import datetime

from pydantic import BaseModel


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


class AdminUpdateRoleRequest(BaseModel):
    role: str


class AdminUserResponse(UserResponse):
    """Extended user response for admin views."""

    status: str
    last_login_at: datetime | None
    updated_at: datetime

    model_config = {"from_attributes": True}
