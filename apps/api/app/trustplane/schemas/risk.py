"""Pydantic schemas for Risk Classification (ADR-017 Part B)."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, field_validator

from app.schemas.base import (
    reject_ctrl_json,
    reject_ctrl_str,
    reject_deep_json,
    reject_nonfinite_json,
)

VALID_RISK_TIERS = {"minimal", "low", "medium", "high", "critical"}
VALID_ASSESSMENT_STATUSES = {"draft", "submitted", "approved", "rejected", "superseded"}


# ── Assessment schemas ───────────────────────────────────────────────


class CreateAssessmentRequest(BaseModel):
    dimension_scores: dict
    policy_id: str | None = None

    @field_validator("dimension_scores")
    @classmethod
    def validate_dimension_scores(cls, v):
        reject_ctrl_json(v, "dimension_scores")
        reject_deep_json(v, "dimension_scores", limit=4)
        reject_nonfinite_json(v, "dimension_scores")
        if not v:
            raise ValueError("dimension_scores must not be empty")
        for key, score in v.items():
            if not isinstance(score, (int, float)):
                raise ValueError(f"dimension_scores.{key} must be a number")
            if score < 1 or score > 5:
                raise ValueError(f"dimension_scores.{key} must be between 1 and 5")
        return v


class ReviewDecisionRequest(BaseModel):
    justification: str | None = None

    @field_validator("justification")
    @classmethod
    def validate_justification(cls, v):
        if v is not None:
            v = reject_ctrl_str(v, "justification")
        return v


class RejectAssessmentRequest(BaseModel):
    justification: str

    @field_validator("justification")
    @classmethod
    def validate_justification(cls, v):
        v = reject_ctrl_str(v, "justification")
        if not v or not v.strip():
            raise ValueError("justification must not be empty")
        return v


class OverrideTierRequest(BaseModel):
    tier: str
    justification: str

    @field_validator("tier")
    @classmethod
    def validate_tier(cls, v):
        if v not in VALID_RISK_TIERS:
            raise ValueError(f"tier must be one of: {', '.join(sorted(VALID_RISK_TIERS))}")
        return v

    @field_validator("justification")
    @classmethod
    def validate_justification(cls, v):
        v = reject_ctrl_str(v, "justification")
        if not v or not v.strip():
            raise ValueError("justification must not be empty")
        return v


class AssessmentResponse(BaseModel):
    id: str
    system_id: str
    policy_id: str
    version: int
    status: str
    dimension_scores: dict
    weighted_score: Decimal | None
    computed_tier: str | None
    override_tier: str | None
    effective_tier: str | None
    justification: str | None
    assessed_by: str
    reviewed_by: str | None
    submitted_at: datetime | None
    reviewed_at: datetime | None
    created_at: datetime

    model_config = {"from_attributes": True}


class AssessmentSummaryResponse(BaseModel):
    id: str
    system_id: str
    version: int
    status: str
    weighted_score: Decimal | None
    effective_tier: str | None
    assessed_by: str
    reviewed_by: str | None
    created_at: datetime

    model_config = {"from_attributes": True}


# ── Policy schemas ───────────────────────────────────────────────────


class CreatePolicyRequest(BaseModel):
    name: str
    dimensions: list[dict]
    tier_thresholds: dict

    @field_validator("name")
    @classmethod
    def validate_name(cls, v):
        v = reject_ctrl_str(v, "name")
        if not v or not v.strip():
            raise ValueError("name must not be empty")
        if len(v) > 200:
            raise ValueError("name must be 200 characters or fewer")
        return v.strip()

    @field_validator("dimensions")
    @classmethod
    def validate_dimensions(cls, v):
        reject_ctrl_json(v, "dimensions")
        reject_deep_json(v, "dimensions")
        reject_nonfinite_json(v, "dimensions")
        if not v:
            raise ValueError("dimensions must not be empty")
        keys = set()
        for dim in v:
            if not isinstance(dim, dict):
                raise ValueError("each dimension must be a dict")
            for req in ("key", "label", "weight"):
                if req not in dim:
                    raise ValueError(f"each dimension must have a '{req}' field")
            if dim["key"] in keys:
                raise ValueError(f"duplicate dimension key: {dim['key']}")
            keys.add(dim["key"])
            w = dim["weight"]
            if not isinstance(w, (int, float)) or w <= 0:
                raise ValueError(f"dimension '{dim['key']}' weight must be a positive number")
        return v

    @field_validator("tier_thresholds")
    @classmethod
    def validate_tier_thresholds(cls, v):
        reject_ctrl_json(v, "tier_thresholds")
        reject_deep_json(v, "tier_thresholds", limit=4)
        reject_nonfinite_json(v, "tier_thresholds")
        required = {"minimal", "low", "medium", "high", "critical"}
        if set(v.keys()) != required:
            raise ValueError(f"tier_thresholds must have keys: {', '.join(sorted(required))}")
        return v


class PolicyResponse(BaseModel):
    id: str
    org_id: str | None
    name: str
    version: int
    is_active: bool
    dimensions: list
    tier_thresholds: dict
    created_by: str | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# ── Audit schemas ────────────────────────────────────────────────────


class TrustAuditEventResponse(BaseModel):
    id: str
    org_id: str
    actor_user_id: str | None
    actor_type: str
    action: str
    target_type: str
    target_id: str
    before: dict | None
    after: dict | None
    reason: str | None
    created_at: datetime

    model_config = {"from_attributes": True}
