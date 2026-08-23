"""Schemas for composers + creator assignments (ADR-013)."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, field_validator


class ComposeRequest(BaseModel):
    profile_id: str


class UpdateDraftRequest(BaseModel):
    remove_entity_ids: list[str] = []

    @field_validator("remove_entity_ids")
    @classmethod
    def validate_ids(cls, v: list) -> list:
        if len(v) > 100:
            raise ValueError("Too many entity ids")
        return v


class DraftResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    org_id: str
    draft_type: str
    requirement_profile_id: str | None = None
    match_run_id: str | None = None
    payload: dict
    engine_version: str
    status: str
    confirmed_by: str | None = None
    confirmed_at: datetime | None = None
    materialized_entity_id: str | None = None
    created_at: datetime


class ConfirmResponse(BaseModel):
    draft: DraftResponse
    materialized_entity_id: str


class OfferAssignmentRequest(BaseModel):
    project_id: str
    user_id: str
    match_run_id: str | None = None
    override_reason: str | None = None

    @field_validator("override_reason")
    @classmethod
    def validate_reason(cls, v: str | None) -> str | None:
        if v is not None and len(v) > 2000:
            raise ValueError("Override reason must be 2,000 characters or less")
        return v


class RespondRequest(BaseModel):
    accept: bool


class AssignmentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    org_id: str
    project_id: str
    user_id: str
    match_run_id: str | None = None
    status: str
    assigned_by: str
    override_reason: str | None = None
    responded_at: datetime | None = None
    created_at: datetime


class ShortlistCreator(BaseModel):
    entity_id: str
    name: str | None = None
    rank: int | None = None
    score: float | None = None
    tier: str | None = None
    reasons: list = []
    gaps: list = []
    evidence: dict = {}  # {capability: [{evidence_type, score, occurred_at}]}


class ShortlistResponse(BaseModel):
    match_run_id: str
    engine_version: str
    results: list[ShortlistCreator] = []
    excluded: list[dict] = []
