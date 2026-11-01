"""Pydantic schemas for Release Gates & Runtime Guardrails (ADR-017 Parts D, F)."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, field_validator

from app.schemas.base import (
    reject_ctrl_json,
    reject_ctrl_str,
    reject_deep_json,
    reject_nonfinite_json,
)

VALID_GATE_TRIGGERS = {
    "publish_pack", "approve_app", "install_tenant", "enable_provider",
    "promote_experiment", "increase_autonomy", "accept_federated", "deploy_system",
}
VALID_CHECK_TYPES = {"deterministic", "evaluation", "policy", "human_review", "evidence_required"}
VALID_GATE_OUTCOMES = {"pending", "passed", "failed", "skipped", "overridden"}
VALID_PROFILE_STATUSES = {"draft", "active", "deprecated"}
VALID_GUARDRAIL_TYPES = {
    "tool_allowlist", "permission_boundary", "data_loss_prevention",
    "egress_restriction", "output_schema", "action_budget",
    "rate_limit", "spend_ceiling", "human_confirmation", "content_filter",
}
VALID_GUARDRAIL_STATUSES = {"draft", "active", "disabled"}
VALID_EVAL_VERDICTS = {"allowed", "blocked", "escalated", "rate_limited"}
VALID_BOUNDARY_TYPES = {"spend_ceiling", "action_budget", "rate_limit"}


# ── Assurance Profile schemas ────────────────────────────────────────


class CreateProfileRequest(BaseModel):
    name: str
    trigger: str
    description: str | None = None

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        v = reject_ctrl_str(v, "name")
        if not v or not v.strip():
            raise ValueError("name must not be empty")
        if len(v) > 200:
            raise ValueError("name must be 200 characters or fewer")
        return v.strip()

    @field_validator("trigger")
    @classmethod
    def validate_trigger(cls, v: str) -> str:
        if v not in VALID_GATE_TRIGGERS:
            raise ValueError(f"trigger must be one of: {', '.join(sorted(VALID_GATE_TRIGGERS))}")
        return v

    @field_validator("description")
    @classmethod
    def validate_description(cls, v: str | None) -> str | None:
        if v is not None:
            v = reject_ctrl_str(v, "description")
        return v


class ProfileResponse(BaseModel):
    id: str
    org_id: str | None
    name: str
    description: str | None
    trigger: str
    status: str
    version: int
    created_by: str | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# ── Gate Check schemas ───────────────────────────────────────────────


class AddCheckRequest(BaseModel):
    name: str
    check_type: str
    is_blocking: bool = True
    config: dict | None = None
    description: str | None = None

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        v = reject_ctrl_str(v, "name")
        if not v or not v.strip():
            raise ValueError("name must not be empty")
        return v.strip()

    @field_validator("check_type")
    @classmethod
    def validate_check_type(cls, v: str) -> str:
        if v not in VALID_CHECK_TYPES:
            raise ValueError(f"check_type must be one of: {', '.join(sorted(VALID_CHECK_TYPES))}")
        return v

    @field_validator("config")
    @classmethod
    def validate_config(cls, v: dict | None) -> dict | None:
        if v is not None:
            reject_ctrl_json(v, "config")
            reject_deep_json(v, "config")
            reject_nonfinite_json(v, "config")
        return v


class CheckResponse(BaseModel):
    id: str
    profile_id: str
    name: str
    description: str | None
    check_type: str
    is_blocking: bool
    config: dict
    ordinal: int
    created_at: datetime

    model_config = {"from_attributes": True}


# ── Gate Result schemas ──────────────────────────────────────────────


class EvaluateGateRequest(BaseModel):
    profile_id: str
    target_type: str
    target_id: str
    target_version: str | None = None
    check_results: list[dict]

    @field_validator("check_results")
    @classmethod
    def validate_check_results(cls, v: list) -> list:
        reject_ctrl_json(v, "check_results")
        reject_deep_json(v, "check_results")
        for cr in v:
            if not isinstance(cr, dict):
                raise ValueError("each check_result must be a dict")
            if "check_id" not in cr or "outcome" not in cr:
                raise ValueError("each check_result must have check_id and outcome")
            if cr["outcome"] not in {"passed", "failed", "skipped"}:
                raise ValueError("check_result outcome must be passed, failed, or skipped")
        return v


class OverrideGateRequest(BaseModel):
    justification: str

    @field_validator("justification")
    @classmethod
    def validate_justification(cls, v: str) -> str:
        v = reject_ctrl_str(v, "justification")
        if not v or not v.strip():
            raise ValueError("justification must not be empty")
        return v


class GateResultResponse(BaseModel):
    id: str
    org_id: str
    profile_id: str
    target_type: str
    target_id: str
    target_version: str | None
    outcome: str
    check_results: list
    override_justification: str | None
    override_by: str | None
    evaluated_by: str | None
    created_at: datetime

    model_config = {"from_attributes": True}


# ── Guardrail Policy schemas ────────────────────────────────────────


class CreateGuardrailRequest(BaseModel):
    name: str
    guardrail_type: str
    config: dict
    system_id: str | None = None
    description: str | None = None
    is_blocking: bool = True
    priority: int = 100

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        v = reject_ctrl_str(v, "name")
        if not v or not v.strip():
            raise ValueError("name must not be empty")
        return v.strip()

    @field_validator("guardrail_type")
    @classmethod
    def validate_guardrail_type(cls, v: str) -> str:
        if v not in VALID_GUARDRAIL_TYPES:
            raise ValueError(f"guardrail_type must be one of: {', '.join(sorted(VALID_GUARDRAIL_TYPES))}")
        return v

    @field_validator("config")
    @classmethod
    def validate_config(cls, v: dict) -> dict:
        reject_ctrl_json(v, "config")
        reject_deep_json(v, "config")
        reject_nonfinite_json(v, "config")
        return v


class GuardrailResponse(BaseModel):
    id: str
    org_id: str
    system_id: str | None
    name: str
    description: str | None
    guardrail_type: str
    status: str
    version: int
    config: dict
    is_blocking: bool
    priority: int
    created_by: str | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class GuardrailSummaryResponse(BaseModel):
    id: str
    name: str
    guardrail_type: str
    status: str
    is_blocking: bool
    priority: int
    system_id: str | None
    created_at: datetime

    model_config = {"from_attributes": True}


# ── Guardrail Evaluation schemas ─────────────────────────────────────


class GuardrailEvalResponse(BaseModel):
    id: str
    org_id: str
    policy_id: str
    policy_version: int
    run_id: str | None
    step_id: str | None
    system_id: str | None
    verdict: str
    reason: str | None
    created_at: datetime

    model_config = {"from_attributes": True}


# ── Action Boundary schemas ──────────────────────────────────────────


class CreateBoundaryRequest(BaseModel):
    name: str
    boundary_type: str
    limit_value: int
    limit_period: str | None = None
    system_id: str | None = None

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        v = reject_ctrl_str(v, "name")
        if not v or not v.strip():
            raise ValueError("name must not be empty")
        return v.strip()

    @field_validator("boundary_type")
    @classmethod
    def validate_boundary_type(cls, v: str) -> str:
        if v not in VALID_BOUNDARY_TYPES:
            raise ValueError(f"boundary_type must be one of: {', '.join(sorted(VALID_BOUNDARY_TYPES))}")
        return v

    @field_validator("limit_value")
    @classmethod
    def validate_limit(cls, v: int) -> int:
        if v <= 0:
            raise ValueError("limit_value must be positive")
        return v

    @field_validator("limit_period")
    @classmethod
    def validate_period(cls, v: str | None) -> str | None:
        if v is not None and v not in {"hour", "day", "week", "month"}:
            raise ValueError("limit_period must be hour, day, week, or month")
        return v


class BoundaryResponse(BaseModel):
    id: str
    org_id: str
    system_id: str | None
    name: str
    boundary_type: str
    limit_value: int
    limit_period: str | None
    current_usage: int
    is_active: bool
    created_by: str | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
