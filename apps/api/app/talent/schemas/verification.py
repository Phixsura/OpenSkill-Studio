"""Pydantic schemas for employer verification, internship supervision, and cohort exposure."""

from datetime import datetime

from pydantic import BaseModel, Field, field_validator

from app.schemas.base import reject_ctrl_json, reject_ctrl_str, reject_nonfinite_json

# ── Employer Verification ──


class CreateVerificationRequest(BaseModel):
    capability_ratings: list[dict] = Field(default_factory=list)
    overall_rating: float | None = Field(None, ge=0, le=5)
    overall_comment: str | None = Field(None, max_length=5000)

    @field_validator("capability_ratings")
    @classmethod
    def _clean_ratings(cls, v):
        v = reject_ctrl_json(v, "capability_ratings")
        return reject_nonfinite_json(v, "capability_ratings")

    @field_validator("overall_comment")
    @classmethod
    def _clean_comment(cls, v):
        if v is not None:
            v = reject_ctrl_str(v, "overall_comment")
        return v


class VerificationResponse(BaseModel):
    id: str
    placement_id: str
    employer_org_id: str
    user_id: str
    capability_ratings: list[dict]
    overall_rating: float | None
    overall_comment: str | None
    created_at: datetime | None = None

    model_config = {"from_attributes": True}


# ── Internship Supervision ──


class CreateSupervisionRequest(BaseModel):
    placement_id: str
    school_org_id: str
    supervisor_user_id: str | None = None
    employer_mentor_name: str | None = Field(None, max_length=100)

    @field_validator("employer_mentor_name")
    @classmethod
    def _clean_mentor(cls, v):
        if v is not None:
            v = reject_ctrl_str(v, "employer_mentor_name")
        return v


class UpdateSupervisionRequest(BaseModel):
    milestones: list[dict] | None = None
    notes: list[dict] | None = None
    status: str | None = None
    supervisor_user_id: str | None = None
    employer_mentor_name: str | None = None

    @field_validator("milestones", "notes")
    @classmethod
    def _clean_json_lists(cls, v, info):
        if v is not None:
            v = reject_ctrl_json(v, info.field_name)
            v = reject_nonfinite_json(v, info.field_name)
        return v


class SupervisionResponse(BaseModel):
    id: str
    placement_id: str
    school_org_id: str
    supervisor_user_id: str | None
    employer_mentor_name: str | None
    milestones: list[dict]
    notes: list[dict]
    status: str
    created_at: datetime | None = None
    updated_at: datetime | None = None

    model_config = {"from_attributes": True}


# ── Cohort Exposure ──


class ExposeOpportunityRequest(BaseModel):
    opportunity_id: str
    note: str | None = Field(None, max_length=2000)

    @field_validator("note")
    @classmethod
    def _clean_note(cls, v):
        if v is not None:
            v = reject_ctrl_str(v, "note")
        return v


class CohortExposureResponse(BaseModel):
    id: str
    cohort_id: str
    opportunity_id: str
    exposed_by: str
    note: str | None
    created_at: datetime | None = None

    model_config = {"from_attributes": True}
