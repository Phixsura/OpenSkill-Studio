"""Pydantic schemas for talent pools, outreach, and outcome events."""

from datetime import datetime

from pydantic import BaseModel, Field, field_validator

from app.schemas.base import reject_ctrl_json, reject_ctrl_str, reject_nonfinite_json

# ---------------------------------------------------------------------------
# Talent Pool
# ---------------------------------------------------------------------------


class CreatePoolRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    description: str | None = Field(None, max_length=5000)
    membership_mode: str = Field("manual", pattern=r"^(manual|rule_suggested|candidate_opt_in)$")
    rule_config: dict | None = Field(None)
    visibility: str = Field("internal", pattern=r"^(internal|shared)$")

    @field_validator("name")
    @classmethod
    def _clean_name(cls, v: str) -> str:
        return reject_ctrl_str(v, "name")

    @field_validator("rule_config")
    @classmethod
    def _clean_rule(cls, v):
        if v is not None:
            v = reject_ctrl_json(v, "rule_config")
            v = reject_nonfinite_json(v, "rule_config")
        return v


class UpdatePoolRequest(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=200)
    description: str | None = Field(None, max_length=5000)
    membership_mode: str | None = Field(None, max_length=500)
    rule_config: dict | None = Field(None)
    visibility: str | None = Field(None, max_length=500)


class PoolResponse(BaseModel):
    id: str
    org_id: str
    name: str
    description: str | None
    membership_mode: str
    rule_config: dict | None
    visibility: str
    created_by: str | None
    created_at: datetime | None = None
    updated_at: datetime | None = None

    model_config = {"from_attributes": True}


# ---------------------------------------------------------------------------
# Pool Membership
# ---------------------------------------------------------------------------


class AddMemberRequest(BaseModel):
    user_id: str
    source: str = Field("manual_added", pattern=r"^(manual_added|rule_suggested|opted_in)$")


class RespondMembershipRequest(BaseModel):
    accept: bool


class MembershipResponse(BaseModel):
    id: str
    pool_id: str
    user_id: str
    source: str
    consent_status: str
    added_by: str | None
    created_at: datetime | None = None

    model_config = {"from_attributes": True}


# ---------------------------------------------------------------------------
# Outreach
# ---------------------------------------------------------------------------


class SendOutreachRequest(BaseModel):
    user_id: str
    outreach_type: str = Field(..., pattern=r"^(opportunity_invitation|pool_invitation)$")
    target_type: str = Field(..., min_length=1, max_length=20)
    target_id: str
    message: str | None = Field(None, max_length=5000)
    expires_at: datetime | None = None

    @field_validator("message")
    @classmethod
    def _clean_message(cls, v):
        if v is not None:
            v = reject_ctrl_str(v, "message")
        return v


class RespondOutreachRequest(BaseModel):
    status: str = Field(..., pattern=r"^(accepted|declined)$")


class OutreachResponse(BaseModel):
    id: str
    org_id: str
    user_id: str
    outreach_type: str
    target_type: str
    target_id: str
    status: str
    message: str | None
    sent_at: datetime
    responded_at: datetime | None
    expires_at: datetime | None
    created_at: datetime | None = None

    model_config = {"from_attributes": True}


# ---------------------------------------------------------------------------
# Outcome Events
# ---------------------------------------------------------------------------


class RecordOutcomeRequest(BaseModel):
    event_type: str = Field(..., min_length=1, max_length=40)
    source_type: str | None = Field(None, max_length=30)
    source_id: str | None = None
    occurred_at: datetime
    visibility: str = Field("private", pattern=r"^(private|passport_visible|public)$")
    metadata: dict | None = Field(None)

    @field_validator("metadata")
    @classmethod
    def _clean_metadata(cls, v):
        if v is not None:
            v = reject_ctrl_json(v, "metadata")
            v = reject_nonfinite_json(v, "metadata")
        return v


class UpdateOutcomeVisibilityRequest(BaseModel):
    visibility: str = Field(..., pattern=r"^(private|passport_visible|public)$")


class OutcomeEventResponse(BaseModel):
    id: str
    user_id: str
    event_type: str
    source_type: str | None
    source_id: str | None
    visibility: str
    metadata: dict = Field(default_factory=dict, validation_alias="extra")
    occurred_at: datetime
    created_at: datetime | None = None

    model_config = {"from_attributes": True, "populate_by_name": True}
