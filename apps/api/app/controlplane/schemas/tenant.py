"""Tenant / platform-role / impersonation / audit schemas (ADR-014 §1)."""

from datetime import datetime

from pydantic import BaseModel, EmailStr, Field, field_validator

from app.schemas.base import reject_ctrl_str

# ── Requests ─────────────────────────────────────────────────


class CreateTenantRequest(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    slug: str = Field(min_length=2, max_length=100, pattern=r"^[a-z0-9][a-z0-9-]*$")
    account_type: str = "direct"
    currency: str = Field(default="USD", pattern=r"^[A-Z]{3}$")
    timezone: str = Field(default="UTC", max_length=50)
    billing_email: EmailStr | None = None
    country: str | None = Field(default=None, pattern=r"^[A-Z]{2}$")

    @field_validator("name", "timezone")
    @classmethod
    def _ctrl(cls, v, info):
        return reject_ctrl_str(v, info.field_name)


class UpdateTenantRequest(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=200)
    billing_email: EmailStr | None = None
    timezone: str | None = Field(default=None, max_length=50)
    country: str | None = Field(default=None, pattern=r"^[A-Z]{2}$")

    @field_validator("name", "timezone")
    @classmethod
    def _ctrl(cls, v, info):
        return reject_ctrl_str(v, info.field_name)


class SuspendTenantRequest(BaseModel):
    reason: str = Field(min_length=3, max_length=500)

    @field_validator("reason")
    @classmethod
    def _ctrl(cls, v, info):
        return reject_ctrl_str(v, info.field_name)


class AddTenantMemberRequest(BaseModel):
    user_id: str = Field(min_length=26, max_length=26)
    role: str  # owner | billing_admin


class GrantPlatformRoleRequest(BaseModel):
    user_id: str = Field(min_length=26, max_length=26)
    role: str  # platform_admin | platform_support | billing_admin


class CreateImpersonationGrantRequest(BaseModel):
    target_user_id: str = Field(min_length=26, max_length=26)
    tenant_id: str | None = Field(default=None, min_length=26, max_length=26)
    reason: str = Field(min_length=10, max_length=500)
    expires_in_minutes: int = Field(default=60, ge=1, le=60)

    @field_validator("reason")
    @classmethod
    def _ctrl(cls, v, info):
        return reject_ctrl_str(v, info.field_name)


class CreateOrgUnderTenantRequest(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    slug: str = Field(min_length=2, max_length=100, pattern=r"^[a-z0-9][a-z0-9-]*$")
    description: str | None = Field(default=None, max_length=2000)

    @field_validator("name", "description")
    @classmethod
    def _ctrl(cls, v, info):
        return reject_ctrl_str(v, info.field_name)


# ── Responses ────────────────────────────────────────────────


class TenantResponse(BaseModel):
    id: str
    name: str
    slug: str
    status: str
    trial_ends_at: datetime | None
    account_type: str
    billing_email: str | None
    country: str | None
    currency: str
    timezone: str
    partner_id: str | None
    suspended_at: datetime | None
    suspension_reason: str | None
    created_at: datetime

    model_config = {"from_attributes": True}


class TenantMemberResponse(BaseModel):
    id: str
    tenant_id: str
    user_id: str
    role: str
    created_at: datetime

    model_config = {"from_attributes": True}


class PlatformRoleResponse(BaseModel):
    id: str
    user_id: str
    role: str
    created_at: datetime

    model_config = {"from_attributes": True}


class ImpersonationGrantResponse(BaseModel):
    id: str
    platform_user_id: str
    target_user_id: str
    tenant_id: str | None
    reason: str
    expires_at: datetime
    revoked_at: datetime | None
    used_count: int
    created_at: datetime

    model_config = {"from_attributes": True}


class ImpersonationTokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int


class AuditEventResponse(BaseModel):
    id: str
    actor_user_id: str | None
    actor_type: str
    action: str
    target_type: str
    target_id: str
    tenant_id: str | None
    partner_id: str | None
    before: dict | None
    after: dict | None
    reason: str | None
    request_id: str | None
    created_at: datetime

    model_config = {"from_attributes": True}


class TenantMembershipSummary(BaseModel):
    """Embedded in MeResponse (§1.6)."""

    tenant_id: str
    slug: str
    name: str
    role: str
    status: str


class PartnerMembershipSummary(BaseModel):
    partner_id: str
    name: str
    role: str


class ImpersonationInfo(BaseModel):
    grant_id: str
    platform_user_id: str
