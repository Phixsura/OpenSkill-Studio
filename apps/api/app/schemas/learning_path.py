"""Pydantic schemas for learning path management."""

from datetime import datetime

from pydantic import BaseModel, field_validator


class CreateLearningPathRequest(BaseModel):
    name: str
    description: str | None = None
    estimated_minutes: int | None = None

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        v = v.strip()
        if len(v) < 2 or len(v) > 200:
            raise ValueError("Name must be 2-200 characters")
        return v


class UpdateLearningPathRequest(BaseModel):
    name: str | None = None
    description: str | None = None
    status: str | None = None
    estimated_minutes: int | None = None

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str | None) -> str | None:
        if v is not None:
            v = v.strip()
            if len(v) < 2 or len(v) > 200:
                raise ValueError("Name must be 2-200 characters")
        return v

    @field_validator("status")
    @classmethod
    def validate_status(cls, v: str | None) -> str | None:
        if v is not None:
            valid = {"draft", "published", "archived"}
            if v not in valid:
                raise ValueError(f"Status must be one of: {', '.join(sorted(valid))}")
        return v


class LearningPathResponse(BaseModel):
    id: str
    org_id: str
    name: str
    slug: str
    description: str | None
    status: str
    estimated_minutes: int | None
    created_by: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class AddPathItemRequest(BaseModel):
    item_type: str  # skill / project / section
    skill_id: str | None = None
    project_id: str | None = None
    section_title: str | None = None
    sort_order: int = 0
    required: bool = True
    unlock_rule: str = "previous_required"


class PathItemResponse(BaseModel):
    id: str
    path_id: str
    item_type: str
    skill_id: str | None
    project_id: str | None
    section_title: str | None
    sort_order: int
    required: bool
    unlock_rule: str

    model_config = {"from_attributes": True}


class AssignPathRequest(BaseModel):
    path_id: str
