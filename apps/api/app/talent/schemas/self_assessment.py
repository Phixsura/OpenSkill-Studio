"""Pydantic schemas for skill self-assessment (N15)."""

from pydantic import BaseModel, Field


class SubmitAssessmentRequest(BaseModel):
    responses: dict[str, list[int]] = Field(
        ...,
        description="Dimension key → list of 1-5 scores per question",
    )


class DimensionScoreDetail(BaseModel):
    label: str
    weight: float
    score: float
    raw_avg: float


class AssessmentResultResponse(BaseModel):
    model_config = {"from_attributes": True}
    evidence_id: str
    capability_id: str
    composite_score: float
    dimension_scores: dict[str, DimensionScoreDetail]
