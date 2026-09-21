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
    status: str | None = Field(..., max_length=500)
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

    model_config = {"from_attributes": True, "json_schema_extra": {"examples": [{}]}}


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
    status: str | None = Field(None, max_length=500)
    evaluation_notes: dict | None = Field(None)
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


class CreateFeedbackRequest(BaseModel):
    feedback_type: str | None = Field(..., max_length=500)
    content: str = Field(..., min_length=1, max_length=5000)
    visibility: str | None = Field("employer_only", max_length=500)

    @field_validator("feedback_type")
    @classmethod
    def _validate_type(cls, v: str) -> str:
        from app.talent.models.application import FEEDBACK_TYPES

        if v not in FEEDBACK_TYPES:
            raise ValueError(f"Invalid feedback_type: {v}. Must be one of {sorted(FEEDBACK_TYPES)}")
        return v

    @field_validator("visibility")
    @classmethod
    def _validate_visibility(cls, v: str) -> str:
        from app.talent.models.application import FEEDBACK_VISIBILITY

        if v not in FEEDBACK_VISIBILITY:
            raise ValueError(
                f"Invalid visibility: {v}. Must be one of {sorted(FEEDBACK_VISIBILITY)}"
            )
        return v


class UpdateFeedbackVisibilityRequest(BaseModel):
    visibility: str | None = Field(..., max_length=500)

    @field_validator("visibility")
    @classmethod
    def _validate_visibility(cls, v: str) -> str:
        from app.talent.models.application import FEEDBACK_VISIBILITY

        if v not in FEEDBACK_VISIBILITY:
            raise ValueError(
                f"Invalid visibility: {v}. Must be one of {sorted(FEEDBACK_VISIBILITY)}"
            )
        return v


class FeedbackResponse(BaseModel):
    id: str
    application_id: str
    feedback_type: str
    content: str
    visibility: str
    author_id: str
    created_at: datetime | None = None

    model_config = {"from_attributes": True}


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
