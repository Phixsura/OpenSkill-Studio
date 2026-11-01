"""Pydantic schemas for Change Management (ADR-017 Part K)."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, field_validator

from app.schemas.base import reject_ctrl_json, reject_ctrl_str, reject_deep_json

VALID_CHANGE_TYPES = {
    "model_version", "provider_version", "prompt_template", "tool_permission",
    "component_dependency", "data_source", "evaluation_method",
    "intended_use", "deployment_scale", "configuration",
}
VALID_CHANGE_IMPACTS = {"none", "low", "medium", "high", "requires_revalidation"}


class CreateChangeEventRequest(BaseModel):
    system_id: str
    change_type: str
    title: str
    description: str | None = None
    before_value: dict | None = None
    after_value: dict | None = None
    impact: str = "low"

    @field_validator("title")
    @classmethod
    def v_title(cls, v: str) -> str:
        v = reject_ctrl_str(v, "title")
        if not v or not v.strip():
            raise ValueError("title must not be empty")
        return v.strip()

    @field_validator("change_type")
    @classmethod
    def v_type(cls, v: str) -> str:
        if v not in VALID_CHANGE_TYPES:
            raise ValueError(f"change_type must be one of: {', '.join(sorted(VALID_CHANGE_TYPES))}")
        return v

    @field_validator("impact")
    @classmethod
    def v_impact(cls, v: str) -> str:
        if v not in VALID_CHANGE_IMPACTS:
            raise ValueError(f"impact must be one of: {', '.join(sorted(VALID_CHANGE_IMPACTS))}")
        return v

    @field_validator("before_value", "after_value")
    @classmethod
    def v_values(cls, v: dict | None, info) -> dict | None:
        if v is not None:
            reject_ctrl_json(v, info.field_name)
            reject_deep_json(v, info.field_name)
        return v


class ChangeEventResponse(BaseModel):
    id: str
    org_id: str
    system_id: str
    change_type: str
    title: str
    description: str | None
    before_value: dict | None
    after_value: dict | None
    impact: str
    affected_evidence: list
    affected_assessments: list
    requires_revalidation: bool
    revalidation_status: str
    revalidated_at: datetime | None
    revalidated_by: str | None
    detected_by: str
    created_by: str | None
    created_at: datetime
    model_config = {"from_attributes": True}


class ChangeEventSummaryResponse(BaseModel):
    id: str
    system_id: str
    change_type: str
    title: str
    impact: str
    requires_revalidation: bool
    revalidation_status: str
    created_at: datetime
    model_config = {"from_attributes": True}
