"""Schemas for workflow runs, step runs, reviews (ADR-010 D6)."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, field_validator


class CreateRunRequest(BaseModel):
    installation_id: str
    inputs: dict = {}
    idempotency_key: str | None = None

    @field_validator("inputs")
    @classmethod
    def validate_inputs_size(cls, v: dict) -> dict:
        if len(str(v)) > 50000:
            raise ValueError("Inputs too large")
        return v

    @field_validator("idempotency_key")
    @classmethod
    def validate_idem_key(cls, v: str | None) -> str | None:
        if v is not None and (not v.strip() or len(v) > 100):
            raise ValueError("Idempotency key must be 1-100 characters")
        return v


class DecideReviewRequest(BaseModel):
    decision: str  # approved | rejected
    note: str | None = None

    @field_validator("decision")
    @classmethod
    def validate_decision(cls, v: str) -> str:
        if v not in ("approved", "rejected"):
            raise ValueError("Decision must be approved or rejected")
        return v

    @field_validator("note")
    @classmethod
    def validate_note(cls, v: str | None) -> str | None:
        if v is not None and len(v) > 2000:
            raise ValueError("Note must be 2,000 characters or less")
        return v


class StepRunResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    step_id: str
    step_type: str
    status: str
    attempt: int
    max_attempts: int
    output: dict | None = None
    error_code: str | None = None
    error: str | None = None
    offering_id: str | None = None
    started_at: datetime | None = None
    finished_at: datetime | None = None


class RunEventResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    step_id: str | None = None
    event_type: str
    payload: dict
    created_at: datetime


class WorkflowRunResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    org_id: str
    pack_id: str | None = None
    release_id: str | None = None
    installation_id: str | None = None
    inputs: dict
    outputs: dict | None = None
    status: str
    error_code: str | None = None
    error: str | None = None
    created_at: datetime
    started_at: datetime | None = None
    finished_at: datetime | None = None


class WorkflowRunDetailResponse(WorkflowRunResponse):
    step_runs: list[StepRunResponse] = []
    events: list[RunEventResponse] = []


class StepReviewResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    step_run_id: str
    org_id: str
    instructions: str | None = None
    due_at: datetime
    decision: str | None = None
    decision_note: str | None = None
    decided_by: str | None = None
    decided_at: datetime | None = None
    created_at: datetime
