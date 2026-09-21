"""Scorecard request/response schemas (Phase 4D)."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator

# --- Templates ---


class CriterionItem(BaseModel):
    """Single evaluation criterion in a template."""

    name: str
    weight: float = 1.0
    rubric: str | None = None

    @field_validator("weight")
    @classmethod
    def weight_range(cls, v: float) -> float:
        if not 0 < v <= 1:
            raise ValueError("weight must be in (0, 1]")
        return v


class CreateScorecardTemplateRequest(BaseModel):
    name: str | None = Field(..., max_length=500)
    description: str | None = Field(None, max_length=500)
    criteria: list[CriterionItem] = []


class UpdateScorecardTemplateRequest(BaseModel):
    name: str | None = Field(None, max_length=500)
    description: str | None = Field(None, max_length=500)
    criteria: list[CriterionItem] | None = None
    status: str | None = Field(None, max_length=500)

    @field_validator("status")
    @classmethod
    def valid_status(cls, v: str | None) -> str | None:
        if v is not None and v not in ("active", "archived"):
            raise ValueError("status must be 'active' or 'archived'")
        return v


class ScorecardTemplateResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    org_id: str
    name: str
    description: str | None = None
    criteria: list[dict[str, Any]] = []
    status: str
    created_at: datetime | None = None
    updated_at: datetime | None = None


# --- Scorecards ---

VALID_RECOMMENDATIONS = frozenset({"strong_hire", "hire", "no_hire", "strong_no_hire"})


class CreateScorecardRequest(BaseModel):
    template_id: str | None = None
    ratings: dict = Field(default_factory=dict)
    overall_rating: int | None = None
    recommendation: str | None = Field(None, max_length=500)
    notes: str | None = Field(None, max_length=500)

    @field_validator("overall_rating")
    @classmethod
    def rating_range(cls, v: int | None) -> int | None:
        if v is not None and not (1 <= v <= 5):
            raise ValueError("overall_rating must be between 1 and 5")
        return v

    @field_validator("recommendation")
    @classmethod
    def valid_recommendation(cls, v: str | None) -> str | None:
        if v is not None and v not in VALID_RECOMMENDATIONS:
            raise ValueError(f"recommendation must be one of {sorted(VALID_RECOMMENDATIONS)}")
        return v


class UpdateScorecardRequest(BaseModel):
    ratings: dict | None = Field(None)
    overall_rating: int | None = None
    recommendation: str | None = Field(None, max_length=500)
    notes: str | None = Field(None, max_length=500)

    @field_validator("overall_rating")
    @classmethod
    def rating_range(cls, v: int | None) -> int | None:
        if v is not None and not (1 <= v <= 5):
            raise ValueError("overall_rating must be between 1 and 5")
        return v

    @field_validator("recommendation")
    @classmethod
    def valid_recommendation(cls, v: str | None) -> str | None:
        if v is not None and v not in VALID_RECOMMENDATIONS:
            raise ValueError(f"recommendation must be one of {sorted(VALID_RECOMMENDATIONS)}")
        return v


class ScorecardResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    interview_stage_id: str
    template_id: str | None = None
    interviewer_id: str
    ratings: dict[str, Any] = {}
    overall_rating: int | None = None
    recommendation: str | None = None
    notes: str | None = None
    submitted_at: datetime | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None
