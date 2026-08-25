"""Pydantic schemas for client brief management."""

import re
from datetime import UTC, datetime

from pydantic import BaseModel, field_validator


class CreateClientBriefRequest(BaseModel):
    title: str
    client_name: str
    client_industry: str | None = None
    client_website: str | None = None
    brand_guidelines: str | None = None
    project_type: str
    objective: str
    target_audience: str | None = None
    deliverable_specs: list[dict] = []
    tone_and_style: str | None = None
    references: list[dict] = []
    constraints: str | None = None
    budget_range: str | None = None
    timeline: str | None = None
    evaluation_criteria: list[dict] = []

    @field_validator("title")
    @classmethod
    def validate_title(cls, v: str) -> str:
        v = v.strip()
        if len(v) < 2 or len(v) > 300:
            raise ValueError("Title must be 2-300 characters")
        return v

    @field_validator("client_name")
    @classmethod
    def validate_client_name(cls, v: str) -> str:
        v = v.strip()
        if len(v) < 1 or len(v) > 200:
            raise ValueError("Client name must be 1-200 characters")
        return v

    @field_validator("client_industry")
    @classmethod
    def validate_client_industry(cls, v: str | None) -> str | None:
        if v is not None and len(v) > 100:
            raise ValueError("Client industry must be 100 characters or less")
        return v

    @field_validator("project_type")
    @classmethod
    def validate_project_type(cls, v: str) -> str:
        v = v.strip()
        if len(v) < 1 or len(v) > 50:
            raise ValueError("Project type must be 1-50 characters")
        return v

    @field_validator("objective")
    @classmethod
    def validate_objective(cls, v: str) -> str:
        v = v.strip()
        if len(v) < 10:
            raise ValueError("Objective must be at least 10 characters")
        if len(v) > 10000:
            raise ValueError("Objective must be 10,000 characters or less")
        return v

    @field_validator("brand_guidelines", "target_audience", "tone_and_style", "constraints")
    @classmethod
    def validate_text_fields(cls, v: str | None) -> str | None:
        if v is not None and len(v) > 10000:
            raise ValueError("Text field must be 10,000 characters or less")
        return v

    @field_validator("client_website")
    @classmethod
    def validate_website(cls, v: str | None) -> str | None:
        if v is not None and v != "":
            if len(v) > 500:
                raise ValueError("URL must be 500 characters or less")
            if not re.match(r"^https?://", v, re.IGNORECASE):
                raise ValueError("URL must start with http:// or https://")
        return v

    @field_validator("deliverable_specs", "references", "evaluation_criteria")
    @classmethod
    def validate_json_lists(cls, v: list) -> list:
        if len(v) > 50:
            raise ValueError("List must not exceed 50 entries")
        if len(str(v)) > 50000:
            raise ValueError("List data too large")
        return v

    @field_validator("budget_range")
    @classmethod
    def validate_budget_range(cls, v: str | None) -> str | None:
        if v is not None and len(v) > 100:
            raise ValueError("Budget range must be 100 characters or less")
        return v

    @field_validator("timeline")
    @classmethod
    def validate_timeline(cls, v: str | None) -> str | None:
        if v is not None and len(v) > 200:
            raise ValueError("Timeline must be 200 characters or less")
        return v


class UpdateClientBriefRequest(BaseModel):
    title: str | None = None
    client_name: str | None = None
    client_industry: str | None = None
    client_website: str | None = None
    brand_guidelines: str | None = None
    project_type: str | None = None
    objective: str | None = None
    target_audience: str | None = None
    deliverable_specs: list[dict] | None = None
    tone_and_style: str | None = None
    references: list[dict] | None = None
    constraints: str | None = None
    budget_range: str | None = None
    timeline: str | None = None
    evaluation_criteria: list[dict] | None = None
    status: str | None = None

    @field_validator("title")
    @classmethod
    def validate_title(cls, v: str | None) -> str | None:
        if v is not None:
            v = v.strip()
            if len(v) < 2 or len(v) > 300:
                raise ValueError("Title must be 2-300 characters")
        return v

    @field_validator("client_name")
    @classmethod
    def validate_client_name(cls, v: str | None) -> str | None:
        if v is not None:
            v = v.strip()
            if len(v) < 1 or len(v) > 200:
                raise ValueError("Client name must be 1-200 characters")
        return v

    @field_validator("client_industry")
    @classmethod
    def validate_client_industry(cls, v: str | None) -> str | None:
        if v is not None and len(v) > 100:
            raise ValueError("Client industry must be 100 characters or less")
        return v

    @field_validator("project_type")
    @classmethod
    def validate_project_type(cls, v: str | None) -> str | None:
        if v is not None:
            v = v.strip()
            if len(v) < 1 or len(v) > 50:
                raise ValueError("Project type must be 1-50 characters")
        return v

    @field_validator("brand_guidelines", "target_audience", "tone_and_style", "constraints")
    @classmethod
    def validate_text_fields(cls, v: str | None) -> str | None:
        if v is not None and len(v) > 10000:
            raise ValueError("Text field must be 10,000 characters or less")
        return v

    @field_validator("client_website")
    @classmethod
    def validate_website(cls, v: str | None) -> str | None:
        if v is not None and v != "":
            if len(v) > 500:
                raise ValueError("URL must be 500 characters or less")
            if not re.match(r"^https?://", v, re.IGNORECASE):
                raise ValueError("URL must start with http:// or https://")
        return v

    @field_validator("budget_range")
    @classmethod
    def validate_budget_range(cls, v: str | None) -> str | None:
        if v is not None and len(v) > 100:
            raise ValueError("Budget range must be 100 characters or less")
        return v

    @field_validator("timeline")
    @classmethod
    def validate_timeline(cls, v: str | None) -> str | None:
        if v is not None and len(v) > 200:
            raise ValueError("Timeline must be 200 characters or less")
        return v

    @field_validator("status")
    @classmethod
    def validate_status(cls, v: str | None) -> str | None:
        if v is not None:
            valid = {"draft", "open", "assigned", "in_production", "review", "active", "completed", "cancelled", "archived"}
            if v not in valid:
                raise ValueError(f"Status must be one of: {', '.join(sorted(valid))}")
        return v

    @field_validator("objective")
    @classmethod
    def validate_objective(cls, v: str | None) -> str | None:
        if v is not None:
            v = v.strip()
            if len(v) < 10:
                raise ValueError("Objective must be at least 10 characters")
            if len(v) > 10000:
                raise ValueError("Objective must be 10,000 characters or less")
        return v

    @field_validator("deliverable_specs", "references", "evaluation_criteria")
    @classmethod
    def validate_json_lists(cls, v: list | None) -> list | None:
        if v is not None:
            if len(v) > 50:
                raise ValueError("List must not exceed 50 entries")
            if len(str(v)) > 50000:
                raise ValueError("List data too large")
        return v


class ClientBriefResponse(BaseModel):
    id: str
    org_id: str
    title: str
    slug: str
    client_name: str
    client_industry: str | None
    client_website: str | None
    brand_guidelines: str | None
    project_type: str
    objective: str
    target_audience: str | None
    deliverable_specs: list[dict]
    tone_and_style: str | None
    references: list[dict]
    constraints: str | None
    budget_range: str | None
    timeline: str | None
    evaluation_criteria: list[dict]
    status: str
    created_by: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ConvertBriefToProjectRequest(BaseModel):
    """Convert a client brief into a real project."""

    title: str | None = None  # defaults to brief title
    cohort_id: str | None = None
    deadline: datetime | None = None
    late_deadline: datetime | None = None
    max_submissions: int = 0
    rubric: list[dict]

    @field_validator("title")
    @classmethod
    def validate_title(cls, v: str | None) -> str | None:
        if v is not None:
            v = v.strip()
            if len(v) < 2 or len(v) > 200:
                raise ValueError("Title must be 2-200 characters")
        return v

    @field_validator("rubric")
    @classmethod
    def validate_rubric(cls, v: list) -> list:
        if not v:
            raise ValueError("Rubric must have at least one criterion")
        if len(v) > 20:
            raise ValueError("Rubric must have at most 20 criteria")
        for item in v:
            if not isinstance(item, dict) or "criterion" not in item or "max_score" not in item:
                raise ValueError("Each rubric item must have 'criterion' and 'max_score'")
        return v

    @field_validator("deadline", "late_deadline")
    @classmethod
    def normalize_tz(cls, v: datetime | None) -> datetime | None:
        if v is not None and v.tzinfo is None:
            return v.replace(tzinfo=UTC)
        return v

    @field_validator("max_submissions")
    @classmethod
    def validate_max_submissions(cls, v: int) -> int:
        if v < 0 or v > 1000:
            raise ValueError("max_submissions must be between 0 and 1,000")
        return v


class BriefApplicationResponse(BaseModel):
    id: str
    brief_id: str
    user_id: str
    cohort_id: str | None
    status: str
    note: str | None
    applied_at: datetime
    reviewed_at: datetime | None
    user_name: str | None = None

    model_config = {"from_attributes": True}
