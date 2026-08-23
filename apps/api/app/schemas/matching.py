"""Schemas for requirement profiles, matching, feedback (ADR-012)."""

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

_CONTEXTS = ("learning", "production", "commercial_project", "talent_matching")


class CreateProfileRequest(BaseModel):
    context_type: Literal["learning", "production", "commercial_project", "talent_matching"]
    structured_requirements: dict = {}
    raw_request: str | None = None

    @field_validator("raw_request")
    @classmethod
    def validate_raw(cls, v: str | None) -> str | None:
        if v is not None and len(v) > 4000:
            raise ValueError("Raw request must be 4,000 characters or less")
        return v

    @field_validator("structured_requirements")
    @classmethod
    def validate_structured_size(cls, v: dict) -> dict:
        if len(str(v)) > 10000:
            raise ValueError("Structured requirements too large")
        return v


class ExtractRequest(BaseModel):
    context_type: Literal["learning", "production", "commercial_project", "talent_matching"]
    raw_request: str

    @field_validator("raw_request")
    @classmethod
    def validate_raw(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("Raw request is required")
        if len(v) > 4000:
            raise ValueError("Raw request must be 4,000 characters or less")
        return v


class UpdateProfileRequest(BaseModel):
    edits: dict

    @field_validator("edits")
    @classmethod
    def validate_edits_size(cls, v: dict) -> dict:
        if len(str(v)) > 10000:
            raise ValueError("Edits too large")
        return v


class ProfileResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    org_id: str
    user_id: str | None = None
    context_type: str
    raw_request: str | None = None
    source_brief_id: str | None = None
    structured_requirements: dict
    extraction_meta: dict | None = None
    status: str
    confirmed_at: datetime | None = None
    created_at: datetime


class MatchRequest(BaseModel):
    requirement_profile_id: str
    target_entity_type: Literal["workflow_pack", "skill_pack", "project_template", "creator"]
    limit: int = Field(default=20, ge=1, le=50)
    explain: bool = False


class MatchResultItem(BaseModel):
    entity_id: str
    entity_type: str
    name: str | None = None
    rank: int | None = None
    score: float | None = None
    tier: str | None = None
    reasons: list = []
    gaps: list = []
    explain: dict | None = None


class ExcludedItem(BaseModel):
    entity_id: str
    name: str | None = None
    failures: list = []


class MatchRunResponse(BaseModel):
    id: str
    org_id: str
    target_entity_type: str
    engine_version: str
    config_version: int
    candidate_count: int
    excluded_count: int
    created_at: datetime
    results: list[MatchResultItem] = []
    excluded: list[ExcludedItem] = []


class FeedbackEventRequest(BaseModel):
    match_run_id: str | None = None
    entity_type: str
    entity_id: str
    event_type: Literal[
        "opened",
        "accepted",
        "rejected",
        "installed",
        "added_to_path",
        "used_in_project",
        "human_override",
    ]
    rank_position: int | None = None

    @field_validator("entity_type")
    @classmethod
    def validate_entity_type(cls, v: str) -> str:
        if v not in ("workflow_pack", "skill_pack", "project_template", "creator"):
            raise ValueError("Invalid entity type")
        return v
