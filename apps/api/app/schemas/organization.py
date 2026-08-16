from datetime import datetime

from pydantic import BaseModel, EmailStr, field_validator


class CreateOrgRequest(BaseModel):
    name: str
    slug: str | None = None
    description: str | None = None

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        v = v.strip()
        if len(v) < 2:
            raise ValueError("Organization name must be at least 2 characters")
        if len(v) > 100:
            raise ValueError("Organization name must not exceed 100 characters")
        return v

    @field_validator("slug")
    @classmethod
    def validate_slug(cls, v):
        if v is not None and isinstance(v, str) and len(v) > 200:
            raise ValueError("slug must not exceed 200 characters")
        return v

    @field_validator("description")
    @classmethod
    def validate_description(cls, v: str | None) -> str | None:
        if v is not None and len(v) > 2000:
            raise ValueError("Description must not exceed 2000 characters")
        return v


class UpdateOrgRequest(BaseModel):
    name: str | None = None
    description: str | None = None
    logo_url: str | None = None

    @field_validator("description")
    @classmethod
    def validate_description(cls, v: str | None) -> str | None:
        if v is not None and len(v) > 2000:
            raise ValueError("Description must not exceed 2000 characters")
        return v

    @field_validator("logo_url")
    @classmethod
    def validate_logo_url(cls, v: str | None) -> str | None:
        if v is not None and len(v) > 500:
            raise ValueError("Logo Url must not exceed 500 characters")
        return v

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str | None) -> str | None:
        if v is None:
            return v
        v = v.strip()
        if len(v) < 2:
            raise ValueError("Organization name must be at least 2 characters")
        if len(v) > 100:
            raise ValueError("Organization name must not exceed 100 characters")
        return v


class OrgResponse(BaseModel):
    id: str
    name: str
    slug: str
    description: str | None
    logo_url: str | None
    role: str | None = None  # Caller's role in this org
    member_count: int = 0
    created_at: datetime

    model_config = {"from_attributes": True}


class OrgDetailResponse(OrgResponse):
    status: str
    settings: dict
    created_by: str

    model_config = {"from_attributes": True}


class OrgMemberUserResponse(BaseModel):
    id: str
    email: str
    display_name: str
    avatar_url: str | None

    model_config = {"from_attributes": True}


class OrgMemberResponse(BaseModel):
    id: str
    user: OrgMemberUserResponse
    role: str
    status: str
    joined_at: datetime

    model_config = {"from_attributes": True}


class InviteMembersRequest(BaseModel):
    emails: list[EmailStr]
    role: str = "student"

    @field_validator("emails")
    @classmethod
    def validate_emails(cls, v: list) -> list:
        if len(v) == 0:
            raise ValueError("At least one email required")
        if len(v) > 100:
            raise ValueError("Cannot invite more than 100 at once")
        return v


class InviteResponse(BaseModel):
    invited: int
    already_member: int
    already_invited: int


class CreateInviteLinkRequest(BaseModel):
    role: str = "student"
    max_uses: int | None = None
    expires_in_days: int | None = None

    @field_validator("max_uses")
    @classmethod
    def validate_max_uses(cls, v):
        if v is not None and isinstance(v, int) and (v < 1 or v > 10000):
            raise ValueError("max_uses must be between 1 and 10000")
        return v

    @field_validator("expires_in_days")
    @classmethod
    def validate_expires_in_days(cls, v):
        if v is not None and isinstance(v, int) and (v < 1 or v > 365):
            raise ValueError("expires_in_days must be between 1 and 365")
        return v


class InviteLinkResponse(BaseModel):
    id: str
    code: str
    url: str
    role: str
    max_uses: int | None
    use_count: int
    expires_at: datetime | None
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class AcceptInviteRequest(BaseModel):
    token: str


class JoinByCodeRequest(BaseModel):
    code: str


class UpdateMemberRoleRequest(BaseModel):
    role: str


class UpdateOrgSettingsRequest(BaseModel):
    settings: dict

    @field_validator("settings")
    @classmethod
    def validate_settings(cls, v: dict) -> dict:
        # Bound the settings JSON blob so it can't be used for unbounded storage.
        if len(str(v)) > 20000:
            raise ValueError("settings object is too large")
        return v
