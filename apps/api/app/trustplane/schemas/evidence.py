"""Pydantic schemas for Evidence Graph & Human Oversight (ADR-017 Parts C, H)."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, field_validator

from app.schemas.base import (
    reject_ctrl_json,
    reject_ctrl_str,
    reject_deep_json,
    reject_nonfinite_json,
)

VALID_EVIDENCE_TYPES = {
    "benchmark", "experiment", "evaluation", "red_team", "app_review",
    "privacy_assessment", "incident_report", "human_attestation",
    "external_audit", "policy_simulation", "custom",
}
VALID_EVIDENCE_STATUSES = {"draft", "valid", "stale", "revoked", "superseded"}
VALID_CLAIM_STATUSES = {"draft", "active", "challenged", "retired"}
VALID_LINK_RELATIONS = {"supports", "weakens", "mitigates", "depends_on"}
VALID_REVIEW_TYPES = {
    "risk_assessment", "release_gate", "evidence_review",
    "exception_request", "incident_closure", "policy_change",
}
VALID_REVIEW_STATUSES = {
    "pending", "in_review", "approved", "rejected", "returned", "expired", "cancelled",
}
VALID_DECISION_TYPES = {"approve", "reject", "return", "escalate"}


# ── Assurance Case schemas ───────────────────────────────────────────


class CreateCaseRequest(BaseModel):
    system_id: str
    title: str
    claim: str
    description: str | None = None

    @field_validator("title")
    @classmethod
    def validate_title(cls, v: str) -> str:
        v = reject_ctrl_str(v, "title")
        if not v or not v.strip():
            raise ValueError("title must not be empty")
        if len(v) > 300:
            raise ValueError("title must be 300 characters or fewer")
        return v.strip()

    @field_validator("claim")
    @classmethod
    def validate_claim(cls, v: str) -> str:
        v = reject_ctrl_str(v, "claim")
        if not v or not v.strip():
            raise ValueError("claim must not be empty")
        return v

    @field_validator("description")
    @classmethod
    def validate_description(cls, v: str | None) -> str | None:
        if v is not None:
            v = reject_ctrl_str(v, "description")
        return v


class UpdateCaseRequest(BaseModel):
    title: str | None = None
    claim: str | None = None
    description: str | None = None

    @field_validator("title")
    @classmethod
    def validate_title(cls, v: str | None) -> str | None:
        if v is not None:
            v = reject_ctrl_str(v, "title")
            if not v.strip():
                raise ValueError("title must not be empty")
            if len(v) > 300:
                raise ValueError("title must be 300 characters or fewer")
            return v.strip()
        return v

    @field_validator("claim")
    @classmethod
    def validate_claim(cls, v: str | None) -> str | None:
        if v is not None:
            v = reject_ctrl_str(v, "claim")
        return v

    @field_validator("description")
    @classmethod
    def validate_description(cls, v: str | None) -> str | None:
        if v is not None:
            v = reject_ctrl_str(v, "description")
        return v


class ChangeCaseStatusRequest(BaseModel):
    status: str

    @field_validator("status")
    @classmethod
    def validate_status(cls, v: str) -> str:
        if v not in VALID_CLAIM_STATUSES:
            raise ValueError(f"status must be one of: {', '.join(sorted(VALID_CLAIM_STATUSES))}")
        return v


class CaseResponse(BaseModel):
    id: str
    org_id: str
    system_id: str
    title: str
    description: str | None
    claim: str
    status: str
    owner_user_id: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# ── Evidence Item schemas ────────────────────────────────────────────


class CreateEvidenceRequest(BaseModel):
    title: str
    evidence_type: str
    description: str | None = None
    source_type: str | None = None
    source_id: str | None = None
    source_version: str | None = None
    scope: str | None = None
    expires_at: str | None = None
    revalidation_rule: str | None = None
    content: dict | None = None
    content_hash: str | None = None

    @field_validator("title")
    @classmethod
    def validate_title(cls, v: str) -> str:
        v = reject_ctrl_str(v, "title")
        if not v or not v.strip():
            raise ValueError("title must not be empty")
        if len(v) > 300:
            raise ValueError("title must be 300 characters or fewer")
        return v.strip()

    @field_validator("evidence_type")
    @classmethod
    def validate_evidence_type(cls, v: str) -> str:
        if v not in VALID_EVIDENCE_TYPES:
            raise ValueError(f"evidence_type must be one of: {', '.join(sorted(VALID_EVIDENCE_TYPES))}")
        return v

    @field_validator("content")
    @classmethod
    def validate_content(cls, v: dict | None) -> dict | None:
        if v is not None:
            reject_ctrl_json(v, "content")
            reject_deep_json(v, "content")
            reject_nonfinite_json(v, "content")
        return v

    @field_validator("description", "scope", "revalidation_rule")
    @classmethod
    def validate_text_fields(cls, v: str | None, info) -> str | None:
        if v is not None:
            v = reject_ctrl_str(v, info.field_name)
        return v


class ChangeEvidenceStatusRequest(BaseModel):
    status: str

    @field_validator("status")
    @classmethod
    def validate_status(cls, v: str) -> str:
        if v not in VALID_EVIDENCE_STATUSES:
            raise ValueError(f"status must be one of: {', '.join(sorted(VALID_EVIDENCE_STATUSES))}")
        return v


class EvidenceResponse(BaseModel):
    id: str
    org_id: str
    title: str
    description: str | None
    evidence_type: str
    status: str
    version: int
    source_type: str | None
    source_id: str | None
    source_version: str | None
    scope: str | None
    expires_at: datetime | None
    revalidation_rule: str | None
    content_hash: str | None
    collected_by: str | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class EvidenceSummaryResponse(BaseModel):
    id: str
    title: str
    evidence_type: str
    status: str
    version: int
    source_type: str | None
    created_at: datetime

    model_config = {"from_attributes": True}


# ── Evidence Link schemas ────────────────────────────────────────────


class LinkEvidenceRequest(BaseModel):
    evidence_id: str
    relation: str = "supports"
    notes: str | None = None

    @field_validator("relation")
    @classmethod
    def validate_relation(cls, v: str) -> str:
        if v not in VALID_LINK_RELATIONS:
            raise ValueError(f"relation must be one of: {', '.join(sorted(VALID_LINK_RELATIONS))}")
        return v

    @field_validator("notes")
    @classmethod
    def validate_notes(cls, v: str | None) -> str | None:
        if v is not None:
            v = reject_ctrl_str(v, "notes")
        return v


class EvidenceLinkResponse(BaseModel):
    link_id: str
    relation: str
    notes: str | None
    evidence: EvidenceSummaryResponse

    model_config = {"from_attributes": False}


# ── Review schemas ───────────────────────────────────────────────────


class CreateReviewRequest(BaseModel):
    review_type: str
    title: str
    target_type: str
    target_id: str
    description: str | None = None
    assigned_to: str | None = None
    context: dict | None = None
    due_at: str | None = None

    @field_validator("review_type")
    @classmethod
    def validate_review_type(cls, v: str) -> str:
        if v not in VALID_REVIEW_TYPES:
            raise ValueError(f"review_type must be one of: {', '.join(sorted(VALID_REVIEW_TYPES))}")
        return v

    @field_validator("title")
    @classmethod
    def validate_title(cls, v: str) -> str:
        v = reject_ctrl_str(v, "title")
        if not v or not v.strip():
            raise ValueError("title must not be empty")
        if len(v) > 300:
            raise ValueError("title must be 300 characters or fewer")
        return v.strip()

    @field_validator("description")
    @classmethod
    def validate_description(cls, v: str | None) -> str | None:
        if v is not None:
            v = reject_ctrl_str(v, "description")
        return v

    @field_validator("context")
    @classmethod
    def validate_context(cls, v: dict | None) -> dict | None:
        if v is not None:
            reject_ctrl_json(v, "context")
            reject_deep_json(v, "context")
        return v


class DecideReviewRequest(BaseModel):
    decision: str
    rationale: str
    conditions: str | None = None

    @field_validator("decision")
    @classmethod
    def validate_decision(cls, v: str) -> str:
        if v not in VALID_DECISION_TYPES:
            raise ValueError(f"decision must be one of: {', '.join(sorted(VALID_DECISION_TYPES))}")
        return v

    @field_validator("rationale")
    @classmethod
    def validate_rationale(cls, v: str) -> str:
        v = reject_ctrl_str(v, "rationale")
        if not v or not v.strip():
            raise ValueError("rationale must not be empty")
        return v

    @field_validator("conditions")
    @classmethod
    def validate_conditions(cls, v: str | None) -> str | None:
        if v is not None:
            v = reject_ctrl_str(v, "conditions")
        return v


class ReviewResponse(BaseModel):
    id: str
    org_id: str
    review_type: str
    status: str
    title: str
    description: str | None
    target_type: str
    target_id: str
    requested_by: str
    assigned_to: str | None
    due_at: datetime | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ReviewSummaryResponse(BaseModel):
    id: str
    review_type: str
    status: str
    title: str
    target_type: str
    requested_by: str
    assigned_to: str | None
    due_at: datetime | None
    created_at: datetime

    model_config = {"from_attributes": True}


class DecisionResponse(BaseModel):
    id: str
    request_id: str
    decision: str
    reviewer_id: str
    rationale: str
    conditions: str | None
    created_at: datetime

    model_config = {"from_attributes": True}
