"""Pydantic schemas for Threat Modeling & Red-Team (ADR-017 Part E)."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, field_validator

from app.schemas.base import (
    reject_ctrl_json,
    reject_ctrl_str,
    reject_deep_json,
    reject_nonfinite_json,
)

VALID_THREAT_CATEGORIES = {
    "prompt_injection", "indirect_instruction", "data_exfiltration",
    "cross_tenant_leakage", "unsafe_tool_invocation", "privilege_escalation",
    "compromised_component", "dependency_tampering", "untrusted_output",
    "model_drift", "automation_abuse", "custom",
}
VALID_THREAT_SEVERITIES = {"info", "low", "medium", "high", "critical"}
VALID_FINDING_STATUSES = {"open", "mitigated", "accepted", "false_positive", "fixed"}


class CreateThreatModelRequest(BaseModel):
    name: str
    category: str
    system_id: str | None = None
    description: str | None = None
    severity: str = "medium"
    attack_vectors: list[str] | None = None
    preconditions: list[str] | None = None
    mitigations: list[str] | None = None
    affected_components: list[str] | None = None

    @field_validator("name")
    @classmethod
    def v_name(cls, v: str) -> str:
        v = reject_ctrl_str(v, "name")
        if not v or not v.strip():
            raise ValueError("name must not be empty")
        return v.strip()

    @field_validator("category")
    @classmethod
    def v_cat(cls, v: str) -> str:
        if v not in VALID_THREAT_CATEGORIES:
            raise ValueError(f"category must be one of: {', '.join(sorted(VALID_THREAT_CATEGORIES))}")
        return v

    @field_validator("severity")
    @classmethod
    def v_sev(cls, v: str) -> str:
        if v not in VALID_THREAT_SEVERITIES:
            raise ValueError(f"severity must be one of: {', '.join(sorted(VALID_THREAT_SEVERITIES))}")
        return v


class ThreatModelResponse(BaseModel):
    id: str
    org_id: str
    system_id: str | None
    name: str
    description: str | None
    category: str
    attack_vectors: list
    preconditions: list
    mitigations: list
    affected_components: list
    severity: str
    created_by: str | None
    created_at: datetime
    updated_at: datetime
    model_config = {"from_attributes": True}


class CreateSuiteRequest(BaseModel):
    name: str
    threat_model_id: str | None = None
    description: str | None = None
    fixtures: list | None = None
    isolation_config: dict | None = None

    @field_validator("name")
    @classmethod
    def v_name(cls, v: str) -> str:
        v = reject_ctrl_str(v, "name")
        if not v or not v.strip():
            raise ValueError("name must not be empty")
        return v.strip()

    @field_validator("fixtures")
    @classmethod
    def v_fix(cls, v: list | None) -> list | None:
        if v is not None:
            reject_ctrl_json(v, "fixtures")
            reject_deep_json(v, "fixtures")
        return v

    @field_validator("isolation_config")
    @classmethod
    def v_iso(cls, v: dict | None) -> dict | None:
        if v is not None:
            reject_ctrl_json(v, "isolation_config")
            reject_deep_json(v, "isolation_config")
            reject_nonfinite_json(v, "isolation_config")
        return v


class SuiteResponse(BaseModel):
    id: str
    org_id: str
    threat_model_id: str | None
    name: str
    description: str | None
    fixtures: list
    isolation_config: dict
    test_count: int
    created_by: str | None
    created_at: datetime
    updated_at: datetime
    model_config = {"from_attributes": True}


class RunResponse(BaseModel):
    id: str
    org_id: str
    suite_id: str
    system_id: str | None
    status: str
    total_tests: int
    passed: int
    failed: int
    started_by: str | None
    started_at: datetime | None
    finished_at: datetime | None
    created_at: datetime
    model_config = {"from_attributes": True}


class FindingResponse(BaseModel):
    id: str
    run_id: str
    title: str
    description: str | None
    severity: str
    status: str
    category: str | None
    mitigation: str | None
    affected_versions: list | None
    created_at: datetime
    model_config = {"from_attributes": True}
