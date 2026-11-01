"""Pydantic schemas for Governance Templates & Compliance Reporting (ADR-017 Parts L, M, N)."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, field_validator

from app.schemas.base import (
    reject_ctrl_json,
    reject_ctrl_str,
    reject_deep_json,
    reject_nonfinite_json,
)

VALID_TEMPLATE_SCOPES = {"global", "region", "tenant", "capability_class", "deployment_type"}
VALID_TEMPLATE_STATUSES = {"draft", "active", "deprecated"}
VALID_REPORT_TYPES = {
    "system_inventory", "risk_assessments", "approval_history", "assurance_cases",
    "evidence_gaps", "evaluation_results", "data_flow_summary", "human_oversight",
    "incident_summary", "exception_log", "full_compliance",
}
VALID_OVERRIDE_TYPES = {
    "risk_threshold", "gate_requirement", "guardrail_config", "review_requirement",
    "monitoring_config", "data_residency", "retention_policy",
}


# ── Template schemas ─────────────────────────────────────────────────


class CreateTemplateRequest(BaseModel):
    name: str
    scope: str
    config: dict
    scope_value: str | None = None
    description: str | None = None
    parent_template_id: str | None = None
    is_restrictive: bool = False

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        v = reject_ctrl_str(v, "name")
        if not v or not v.strip():
            raise ValueError("name must not be empty")
        return v.strip()

    @field_validator("scope")
    @classmethod
    def validate_scope(cls, v: str) -> str:
        if v not in VALID_TEMPLATE_SCOPES:
            raise ValueError(f"scope must be one of: {', '.join(sorted(VALID_TEMPLATE_SCOPES))}")
        return v

    @field_validator("config")
    @classmethod
    def validate_config(cls, v: dict) -> dict:
        reject_ctrl_json(v, "config")
        reject_deep_json(v, "config")
        reject_nonfinite_json(v, "config")
        return v


class TemplateResponse(BaseModel):
    id: str
    org_id: str | None
    name: str
    description: str | None
    scope: str
    scope_value: str | None
    status: str
    version: int
    config: dict
    parent_template_id: str | None
    is_restrictive: bool
    created_by: str | None
    created_at: datetime
    updated_at: datetime
    model_config = {"from_attributes": True}


class TemplateSummaryResponse(BaseModel):
    id: str
    name: str
    scope: str
    scope_value: str | None
    status: str
    is_restrictive: bool
    created_at: datetime
    model_config = {"from_attributes": True}


# ── Report schemas ───────────────────────────────────────────────────


class CreateReportRequest(BaseModel):
    report_type: str
    title: str
    description: str | None = None
    filters: dict | None = None

    @field_validator("report_type")
    @classmethod
    def validate_type(cls, v: str) -> str:
        if v not in VALID_REPORT_TYPES:
            raise ValueError(f"report_type must be one of: {', '.join(sorted(VALID_REPORT_TYPES))}")
        return v

    @field_validator("title")
    @classmethod
    def validate_title(cls, v: str) -> str:
        v = reject_ctrl_str(v, "title")
        if not v or not v.strip():
            raise ValueError("title must not be empty")
        return v.strip()

    @field_validator("filters")
    @classmethod
    def validate_filters(cls, v: dict | None) -> dict | None:
        if v is not None:
            reject_ctrl_json(v, "filters")
            reject_deep_json(v, "filters")
        return v


class ReportResponse(BaseModel):
    id: str
    org_id: str
    report_type: str
    status: str
    title: str
    description: str | None
    filters: dict | None
    system_count: int | None
    finding_count: int | None
    generated_by: str | None
    generated_at: datetime | None
    created_at: datetime
    model_config = {"from_attributes": True}


class ReportSummaryResponse(BaseModel):
    id: str
    report_type: str
    status: str
    title: str
    system_count: int | None
    finding_count: int | None
    generated_at: datetime | None
    created_at: datetime
    model_config = {"from_attributes": True}


# ── Policy Override schemas ──────────────────────────────────────────


class CreatePolicyOverrideRequest(BaseModel):
    override_type: str
    name: str
    config: dict
    description: str | None = None
    template_id: str | None = None

    @field_validator("override_type")
    @classmethod
    def validate_type(cls, v: str) -> str:
        if v not in VALID_OVERRIDE_TYPES:
            raise ValueError(f"override_type must be one of: {', '.join(sorted(VALID_OVERRIDE_TYPES))}")
        return v

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        v = reject_ctrl_str(v, "name")
        if not v or not v.strip():
            raise ValueError("name must not be empty")
        return v.strip()

    @field_validator("config")
    @classmethod
    def validate_config(cls, v: dict) -> dict:
        reject_ctrl_json(v, "config")
        reject_deep_json(v, "config")
        reject_nonfinite_json(v, "config")
        return v


class PolicyOverrideResponse(BaseModel):
    id: str
    org_id: str
    override_type: str
    name: str
    description: str | None
    config: dict
    template_id: str | None
    is_active: bool
    version: int
    created_by: str | None
    created_at: datetime
    updated_at: datetime
    model_config = {"from_attributes": True}
