"""Pydantic schemas for bulk operations."""

from pydantic import BaseModel, Field, field_validator

from app.talent.schemas.capability import (
    CapabilityResponse,
    CreateCapabilityRequest,
)
from app.talent.schemas.evidence import EvidenceResponse, RecordEvidenceRequest

# ---------------------------------------------------------------------------
# Shared
# ---------------------------------------------------------------------------


class BulkError(BaseModel):
    """A single error within a bulk operation."""

    index: int
    error: str


# ---------------------------------------------------------------------------
# Bulk Capabilities
# ---------------------------------------------------------------------------


class BulkCapabilityRequest(BaseModel):
    items: list[CreateCapabilityRequest] = Field(..., min_length=1)

    @field_validator("items")
    @classmethod
    def max_items(cls, v: list) -> list:
        if len(v) > 100:
            raise ValueError("Maximum 100 items per bulk request")
        return v


class BulkCapabilityResult(BaseModel):
    created: list[CapabilityResponse] = []
    errors: list[BulkError] = []


# ---------------------------------------------------------------------------
# Bulk Evidence
# ---------------------------------------------------------------------------


class BulkEvidenceRequest(BaseModel):
    items: list[RecordEvidenceRequest] = Field(..., min_length=1)

    @field_validator("items")
    @classmethod
    def max_items(cls, v: list) -> list:
        if len(v) > 100:
            raise ValueError("Maximum 100 items per bulk request")
        return v


class BulkEvidenceResult(BaseModel):
    created: list[EvidenceResponse] = []
    errors: list[BulkError] = []


# ---------------------------------------------------------------------------
# Bulk Application Transitions
# ---------------------------------------------------------------------------


class TransitionItem(BaseModel):
    application_id: str
    status: str = Field(..., min_length=1)
    note: str | None = Field(None, max_length=1000)


class BulkTransitionRequest(BaseModel):
    transitions: list[TransitionItem] = Field(..., min_length=1)

    @field_validator("transitions")
    @classmethod
    def max_transitions(cls, v: list) -> list:
        if len(v) > 50:
            raise ValueError("Maximum 50 transitions per bulk request")
        return v


class TransitionResult(BaseModel):
    application_id: str
    from_status: str
    to_status: str


class BulkTransitionResult(BaseModel):
    transitioned: list[TransitionResult] = []
    errors: list[BulkError] = []
