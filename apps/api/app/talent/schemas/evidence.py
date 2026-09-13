"""Pydantic schemas for evidence ledger endpoints."""

from datetime import datetime

from pydantic import BaseModel, Field, field_validator

from app.schemas.base import reject_ctrl_json, reject_nonfinite_json


class RecordEvidenceRequest(BaseModel):
    capability_id: str
    source_type: str = Field(..., min_length=1, max_length=40)
    source_id: str
    verification_level: str = Field(..., min_length=1, max_length=30)
    occurred_at: datetime
    org_id: str | None = None
    score_normalized: float | None = Field(None, ge=0.0, le=1.0)
    confidence: float = Field(1.0, ge=0.0, le=1.0)
    expires_at: datetime | None = None
    metadata: dict | None = None

    @field_validator("metadata")
    @classmethod
    def _clean_metadata(cls, v):
        if v is not None:
            v = reject_ctrl_json(v, "metadata")
            v = reject_nonfinite_json(v, "metadata")
        return v


class VoidEvidenceRequest(BaseModel):
    reason: str | None = Field(None, max_length=500)


class EvidenceResponse(BaseModel):
    id: str
    user_id: str
    capability_id: str
    source_type: str
    source_id: str
    org_id: str | None
    score_normalized: float | None
    confidence: float
    verification_level: str
    occurred_at: datetime
    expires_at: datetime | None
    supersedes_id: str | None
    status: str
    metadata: dict = Field(validation_alias="extra")
    created_at: datetime

    model_config = {"from_attributes": True, "populate_by_name": True}


class ProvenanceResponse(BaseModel):
    chain: list[dict]


class CapabilityScoreResponse(BaseModel):
    capability_id: str
    capability_name: str
    level: int
    level_label: str
    score: float
    confidence: float
    evidence_count: int
    substantial_evidence_count: int
    last_verified_at: datetime | None
    verification_mix: dict[str, int]
    scoring_version: str
    computed_at: datetime
