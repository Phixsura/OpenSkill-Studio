"""Pydantic schemas for application/placement pipeline endpoints."""

from datetime import datetime

from pydantic import BaseModel, Field, field_validator

from app.schemas.base import reject_ctrl_str


class CreateApplicationRequest(BaseModel):
    """Submit an application to an opportunity."""
    selected_credentials: list[str] = Field(default_factory=list)
    selected_projects: list[str] = Field(default_factory=list)
    selected_evidence: list[str] = Field(default_factory=list)
    cover_note: str | None = Field(None, max_length=5000)
    resume_asset_id: str | None = None

    @field_validator("cover_note")
    @classmethod
    def _clean_note(cls, v):
        if v is not None:
            v = reject_ctrl_str(v, "cover_note")
        return v


class TransitionApplicationRequest(BaseModel):
    status: str
    note: str | None = Field(None, max_length=2000)


class ApplicationResponse(BaseModel):
    id: str
    opportunity_id: str
    user_id: str
    evidence_bundle: dict
    passport_snapshot_id: str | None
    match_run_id: str | None
    status: str
    cover_note: str | None
    created_at: datetime | None = None
    updated_at: datetime | None = None

    model_config = {"from_attributes": True}


class ApplicationEventResponse(BaseModel):
    id: str
    application_id: str
    from_status: str
    to_status: str
    acted_by: str
    note: str | None
    created_at: datetime | None = None

    model_config = {"from_attributes": True}


class CreateInterviewRequest(BaseModel):
    stage_type: str = Field(..., min_length=1, max_length=30)
    interviewer_id: str | None = None
    scheduled_at: datetime | None = None


class UpdateInterviewRequest(BaseModel):
    status: str | None = None
    evaluation_notes: dict | None = None
    scheduled_at: datetime | None = None
    completed_at: datetime | None = None


class InterviewStageResponse(BaseModel):
    """Response for interview stages.

    NOTE: evaluation_notes is intentionally EXCLUDED — employer-private.
    """
    id: str
    application_id: str
    stage_type: str
    interviewer_id: str | None
    scheduled_at: datetime | None
    completed_at: datetime | None
    status: str
    created_at: datetime | None = None

    model_config = {"from_attributes": True}


class InterviewStageEmployerResponse(InterviewStageResponse):
    """Full response including evaluation notes — employer-only."""
    evaluation_notes: dict | None = None


class PlacementResponse(BaseModel):
    id: str
    application_id: str
    opportunity_id: str
    user_id: str
    employer_org_id: str
    role_title: str | None
    start_date: datetime | None
    end_date: datetime | None
    placement_source: str | None
    status: str
    created_at: datetime | None = None
    updated_at: datetime | None = None

    model_config = {"from_attributes": True}
