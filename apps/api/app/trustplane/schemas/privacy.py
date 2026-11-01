"""Pydantic schemas for Privacy & Consent (ADR-017 Part G)."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, field_validator

from app.schemas.base import reject_ctrl_json, reject_ctrl_str, reject_deep_json

VALID_PRIVACY_STATUSES = {"draft", "in_review", "approved", "rejected", "requires_changes"}
VALID_DATA_CLASSIFICATIONS = {"public", "internal", "confidential", "sensitive_pii", "highly_sensitive"}
VALID_LEGAL_BASES = {"consent", "contract", "legal_obligation", "vital_interest", "public_interest", "legitimate_interest"}
VALID_CONSENT_STATUSES = {"granted", "denied", "withdrawn", "not_required"}


class CreatePrivacyReviewRequest(BaseModel):
    system_id: str
    title: str
    data_classification: str = "internal"
    data_inputs: list | None = None
    data_outputs: list | None = None
    purpose_limitation: str | None = None
    minimization_measures: list | None = None
    redaction_config: dict | None = None
    retention_policy: dict | None = None
    legal_basis: str | None = None
    legal_basis_detail: str | None = None
    regions: list | None = None
    cross_region_transfers: list | None = None
    provider_data_use: dict | None = None

    @field_validator("title")
    @classmethod
    def v_title(cls, v: str) -> str:
        v = reject_ctrl_str(v, "title")
        if not v or not v.strip():
            raise ValueError("title must not be empty")
        return v.strip()

    @field_validator("data_classification")
    @classmethod
    def v_class(cls, v: str) -> str:
        if v not in VALID_DATA_CLASSIFICATIONS:
            raise ValueError(f"data_classification must be one of: {', '.join(sorted(VALID_DATA_CLASSIFICATIONS))}")
        return v

    @field_validator("legal_basis")
    @classmethod
    def v_basis(cls, v: str | None) -> str | None:
        if v is not None and v not in VALID_LEGAL_BASES:
            raise ValueError(f"legal_basis must be one of: {', '.join(sorted(VALID_LEGAL_BASES))}")
        return v

    @field_validator("data_inputs", "data_outputs", "minimization_measures", "regions", "cross_region_transfers")
    @classmethod
    def v_lists(cls, v: list | None, info) -> list | None:
        if v is not None:
            reject_ctrl_json(v, info.field_name)
            reject_deep_json(v, info.field_name)
        return v

    @field_validator("redaction_config", "retention_policy", "provider_data_use")
    @classmethod
    def v_dicts(cls, v: dict | None, info) -> dict | None:
        if v is not None:
            reject_ctrl_json(v, info.field_name)
            reject_deep_json(v, info.field_name)
        return v


class PrivacyReviewResponse(BaseModel):
    id: str
    org_id: str
    system_id: str
    title: str
    status: str
    data_classification: str
    data_inputs: list
    data_outputs: list
    purpose_limitation: str | None
    minimization_measures: list
    legal_basis: str | None
    regions: list
    cross_region_transfers: list
    reviewed_by: str | None
    created_by: str | None
    created_at: datetime
    updated_at: datetime
    model_config = {"from_attributes": True}


class CreateConsentRecordRequest(BaseModel):
    system_id: str
    purpose: str
    consent_status: str
    data_categories: list | None = None

    @field_validator("purpose")
    @classmethod
    def v_purpose(cls, v: str) -> str:
        v = reject_ctrl_str(v, "purpose")
        if not v or not v.strip():
            raise ValueError("purpose must not be empty")
        return v.strip()

    @field_validator("consent_status")
    @classmethod
    def v_status(cls, v: str) -> str:
        if v not in VALID_CONSENT_STATUSES:
            raise ValueError(f"consent_status must be one of: {', '.join(sorted(VALID_CONSENT_STATUSES))}")
        return v


class ConsentRecordResponse(BaseModel):
    id: str
    org_id: str
    system_id: str
    purpose: str
    consent_status: str
    data_categories: list
    granted_at: datetime | None
    withdrawn_at: datetime | None
    expires_at: datetime | None
    created_at: datetime
    model_config = {"from_attributes": True}
