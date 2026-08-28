"""Schemas for requirement profiles, matching, feedback (ADR-012)."""

import re
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

_CONTEXTS = ("learning", "production", "commercial_project", "talent_matching")

# NUL / C0-C1 control chars would be stored verbatim into JSONB and crash
# asyncpg (UntranslatableCharacterError) at write time — a 500. Reject as
# 422 (tab/newline allowed). Same recursion as schemas/workflow_definition.py:
# scan the ACTUAL string values, not str(v) — repr escapes a NUL to a
# backslash sequence the regex would never match.
_CTRL_RE = re.compile(r"[\x00-\x08\x0b-\x1f\x7f-\x9f]")


_MAX_NESTING = 30  # deeper client payloads are hostile, not requirements


def _has_ctrl(v, depth: int = 0) -> bool:
    # Depth-capped: unbounded recursion on a deeply nested payload raises
    # RecursionError → 500, the exact defect class this validator closes.
    # Structures deeper than any legitimate requirement are rejected outright
    # by treating them as invalid (True → 422).
    # Also screens non-finite floats (NaN/Infinity/-Infinity): stdlib
    # json.loads accepts the bare tokens, they pass every str/size check, and
    # SQLAlchemy's default JSONB serializer (allow_nan=True) re-emits `NaN`/
    # `Infinity` which Postgres rejects (22P02 → DBAPIError → 500). bool is an
    # int subclass, not float, so booleans are unaffected. (R73)
    import math

    if depth > _MAX_NESTING:
        return True
    if isinstance(v, str):
        return bool(_CTRL_RE.search(v))
    if isinstance(v, float):
        return not math.isfinite(v)
    if isinstance(v, dict):
        return any(_has_ctrl(k, depth + 1) or _has_ctrl(val, depth + 1) for k, val in v.items())
    if isinstance(v, list):
        return any(_has_ctrl(x, depth + 1) for x in v)
    return False


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
        if _has_ctrl(v):
            raise ValueError(
                "Structured requirements contain disallowed values "
                "(NUL/control characters, NaN/Infinity, or excessive nesting)"
            )
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
        if _has_ctrl(v):
            raise ValueError(
                "Edits contain disallowed values "
                "(NUL/control characters, NaN/Infinity, or excessive nesting)"
            )
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
    # ULID-sized loose refs / bounded rank — over-length or out-of-int32
    # values must be a clean 422, never an asyncpg
    # StringDataRightTruncation / integer-overflow 500. Negative ranks would
    # pollute the position-bias dataset (R17).
    match_run_id: str | None = Field(default=None, max_length=26)
    entity_type: str
    entity_id: str = Field(min_length=1, max_length=26)
    event_type: Literal[
        "opened",
        "accepted",
        "rejected",
        "installed",
        "added_to_path",
        "used_in_project",
        "human_override",
    ]
    rank_position: int | None = Field(default=None, ge=0, le=1_000_000)

    @field_validator("entity_type")
    @classmethod
    def validate_entity_type(cls, v: str) -> str:
        if v not in ("workflow_pack", "skill_pack", "project_template", "creator"):
            raise ValueError("Invalid entity type")
        return v
