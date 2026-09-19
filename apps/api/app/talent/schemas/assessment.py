"""Pydantic schemas for assessments and credentials endpoints."""

from datetime import datetime

from pydantic import BaseModel, Field, field_validator

from app.schemas.base import reject_ctrl_json, reject_ctrl_str, reject_nonfinite_json


class CreateBlueprintRequest(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: str | None = Field(None, max_length=5000)
    assessment_type: str = Field(..., min_length=1, max_length=30)
    capability_requirements: list[dict] = Field(default_factory=list)
    config: dict = Field(default_factory=dict)

    @field_validator("title")
    @classmethod
    def _clean_title(cls, v):
        return reject_ctrl_str(v, "title")

    @field_validator("config")
    @classmethod
    def _clean_config(cls, v):
        v = reject_ctrl_json(v, "config")
        return reject_nonfinite_json(v, "config")


class UpdateBlueprintRequest(BaseModel):
    title: str | None = Field(None, min_length=1, max_length=200)
    description: str | None = Field(None, max_length=5000)
    assessment_type: str | None = None
    capability_requirements: list[dict] | None = None
    config: dict | None = None
    status: str | None = None


class BlueprintResponse(BaseModel):
    id: str
    org_id: str
    title: str
    description: str | None
    assessment_type: str
    capability_requirements: list[dict]
    config: dict
    version: int
    status: str
    created_by: str | None
    created_at: datetime | None = None
    updated_at: datetime | None = None

    model_config = {"from_attributes": True}


class StartRunRequest(BaseModel):
    pass  # Attempt is auto-numbered


class SubmitRunRequest(BaseModel):
    results: dict | None = None
    project_id: str | None = None


class ReviewRunRequest(BaseModel):
    results: list[dict]  # [{"capability_id": "...", "score": 0.85, "passed": true}]
    status: str  # passed | failed


class RunResponse(BaseModel):
    id: str
    blueprint_id: str
    blueprint_version: int
    user_id: str
    org_id: str
    attempt_number: int
    status: str
    started_at: datetime | None
    submitted_at: datetime | None
    deadline_at: datetime | None
    results: dict | list | None = None
    project_id: str | None
    reviewed_by: str | None
    reviewed_at: datetime | None
    created_at: datetime | None = None

    model_config = {"from_attributes": True}


# Credentials


class CreateCredentialRuleRequest(BaseModel):
    credential_type: str = Field(..., min_length=1, max_length=80)
    display_name: str = Field(..., min_length=1, max_length=200)
    description: str | None = Field(None, max_length=5000)
    requirements: list[dict]
    conditions: dict = Field(default_factory=dict)
    org_id: str | None = None


class CredentialRuleResponse(BaseModel):
    id: str
    credential_type: str
    version: int
    display_name: str
    description: str | None
    requirements: list[dict]
    conditions: dict
    org_id: str | None
    status: str
    activated_at: datetime | None
    created_at: datetime | None = None

    model_config = {"from_attributes": True}


class CredentialResponse(BaseModel):
    id: str
    credential_type: str
    version: int
    credential_rule_id: str | None
    issuer_org_id: str | None
    user_id: str
    capabilities: list[dict]
    evidence_references: list[dict]
    status: str
    issued_at: datetime | None = None
    expires_at: datetime | None
    revalidation_at: datetime | None
    revoked_at: datetime | None
    revoked_reason: str | None = None
    created_at: datetime | None = None

    model_config = {"from_attributes": True}


class EvaluateCredentialRequest(BaseModel):
    credential_type: str
    user_id: str | None = None  # Default: current user


class IssueCredentialRequest(BaseModel):
    credential_type: str
    user_id: str | None = None
    org_id: str | None = None
