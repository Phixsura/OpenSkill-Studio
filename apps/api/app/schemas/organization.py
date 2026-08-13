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


class UpdateOrgRequest(BaseModel):
    name: str | None = None
    description: str | None = None
    logo_url: str | None = None


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
