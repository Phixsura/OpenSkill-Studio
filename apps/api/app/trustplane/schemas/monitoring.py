"""Pydantic schemas for Monitoring & Incidents (ADR-017 Parts I, J)."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, field_validator

from app.schemas.base import (
    reject_ctrl_json,
    reject_ctrl_str,
    reject_deep_json,
    reject_nonfinite_json,
)

VALID_MONITOR_TYPES = {
    "quality_regression", "safety_regression", "behavior_drift", "guardrail_rate",
    "cost_anomaly", "latency_anomaly", "evidence_expiry", "dependency_change",
    "privacy_incident", "custom",
}
VALID_ALERT_SEVERITIES = {"info", "warning", "critical"}
VALID_ALERT_STATUSES = {"open", "acknowledged", "resolved", "suppressed"}
VALID_INCIDENT_SEVERITIES = {"low", "medium", "high", "critical"}
VALID_INCIDENT_STATUSES = {
    "reported", "triaging", "contained", "investigating",
    "remediating", "validating", "closed",
}
VALID_ACTION_TYPES = {
    "pause_capability", "revoke_app", "disable_provider", "rollback_release",
    "restrict_permissions", "containment", "investigation", "remediation",
    "validation", "communication", "post_incident",
}


# ── Monitor schemas ──────────────────────────────────────────────────


class CreateMonitorRequest(BaseModel):
    name: str
    monitor_type: str
    config: dict
    system_id: str | None = None
    description: str | None = None
    alert_severity: str = "warning"
    check_interval_minutes: int = 60

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        v = reject_ctrl_str(v, "name")
        if not v or not v.strip():
            raise ValueError("name must not be empty")
        return v.strip()

    @field_validator("monitor_type")
    @classmethod
    def validate_type(cls, v: str) -> str:
        if v not in VALID_MONITOR_TYPES:
            raise ValueError(f"monitor_type must be one of: {', '.join(sorted(VALID_MONITOR_TYPES))}")
        return v

    @field_validator("config")
    @classmethod
    def validate_config(cls, v: dict) -> dict:
        reject_ctrl_json(v, "config")
        reject_deep_json(v, "config")
        reject_nonfinite_json(v, "config")
        return v

    @field_validator("alert_severity")
    @classmethod
    def validate_severity(cls, v: str) -> str:
        if v not in VALID_ALERT_SEVERITIES:
            raise ValueError(f"alert_severity must be one of: {', '.join(sorted(VALID_ALERT_SEVERITIES))}")
        return v

    @field_validator("check_interval_minutes")
    @classmethod
    def validate_interval(cls, v: int) -> int:
        if v < 1 or v > 10080:
            raise ValueError("check_interval_minutes must be between 1 and 10080")
        return v


class MonitorResponse(BaseModel):
    id: str
    org_id: str
    system_id: str | None
    name: str
    description: str | None
    monitor_type: str
    status: str
    config: dict
    alert_severity: str
    check_interval_minutes: int
    created_by: str | None
    created_at: datetime
    updated_at: datetime
    model_config = {"from_attributes": True}


class MonitorSummaryResponse(BaseModel):
    id: str
    name: str
    monitor_type: str
    status: str
    alert_severity: str
    system_id: str | None
    created_at: datetime
    model_config = {"from_attributes": True}


# ── Alert schemas ────────────────────────────────────────────────────


class AlertResponse(BaseModel):
    id: str
    org_id: str
    monitor_id: str
    system_id: str | None
    severity: str
    status: str
    title: str
    detail: str | None
    metric_value: dict | None
    threshold: dict | None
    incident_id: str | None
    acknowledged_by: str | None
    acknowledged_at: datetime | None
    resolved_at: datetime | None
    created_at: datetime
    model_config = {"from_attributes": True}


# ── Incident schemas ─────────────────────────────────────────────────


class CreateIncidentRequest(BaseModel):
    title: str
    severity: str
    system_id: str | None = None
    description: str | None = None
    impact: dict | None = None
    assigned_to: str | None = None

    @field_validator("title")
    @classmethod
    def validate_title(cls, v: str) -> str:
        v = reject_ctrl_str(v, "title")
        if not v or not v.strip():
            raise ValueError("title must not be empty")
        if len(v) > 300:
            raise ValueError("title must be 300 characters or fewer")
        return v.strip()

    @field_validator("severity")
    @classmethod
    def validate_severity(cls, v: str) -> str:
        if v not in VALID_INCIDENT_SEVERITIES:
            raise ValueError(f"severity must be one of: {', '.join(sorted(VALID_INCIDENT_SEVERITIES))}")
        return v

    @field_validator("impact")
    @classmethod
    def validate_impact(cls, v: dict | None) -> dict | None:
        if v is not None:
            reject_ctrl_json(v, "impact")
            reject_deep_json(v, "impact")
        return v


class ChangeIncidentStatusRequest(BaseModel):
    status: str

    @field_validator("status")
    @classmethod
    def validate_status(cls, v: str) -> str:
        if v not in VALID_INCIDENT_STATUSES:
            raise ValueError(f"status must be one of: {', '.join(sorted(VALID_INCIDENT_STATUSES))}")
        return v


class IncidentResponse(BaseModel):
    id: str
    org_id: str
    system_id: str | None
    title: str
    description: str | None
    severity: str
    status: str
    impact: dict | None
    root_cause: str | None
    resolution: str | None
    reported_by: str
    assigned_to: str | None
    reported_at: datetime
    contained_at: datetime | None
    resolved_at: datetime | None
    closed_at: datetime | None
    created_at: datetime
    updated_at: datetime
    model_config = {"from_attributes": True}


class IncidentSummaryResponse(BaseModel):
    id: str
    title: str
    severity: str
    status: str
    system_id: str | None
    reported_by: str
    reported_at: datetime
    model_config = {"from_attributes": True}


# ── Action schemas ───────────────────────────────────────────────────


class AddActionRequest(BaseModel):
    action_type: str
    title: str
    description: str | None = None
    target_type: str | None = None
    target_id: str | None = None

    @field_validator("action_type")
    @classmethod
    def validate_type(cls, v: str) -> str:
        if v not in VALID_ACTION_TYPES:
            raise ValueError(f"action_type must be one of: {', '.join(sorted(VALID_ACTION_TYPES))}")
        return v

    @field_validator("title")
    @classmethod
    def validate_title(cls, v: str) -> str:
        v = reject_ctrl_str(v, "title")
        if not v or not v.strip():
            raise ValueError("title must not be empty")
        return v.strip()


class ActionResponse(BaseModel):
    id: str
    incident_id: str
    action_type: str
    status: str
    title: str
    description: str | None
    target_type: str | None
    target_id: str | None
    performed_by: str | None
    result: dict | None
    created_at: datetime
    completed_at: datetime | None
    model_config = {"from_attributes": True}
