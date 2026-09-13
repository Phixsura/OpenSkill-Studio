"""Pydantic schemas for learning path management."""

from datetime import datetime

from pydantic import BaseModel, Field, field_validator, model_validator


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

    @field_validator("description")
    @classmethod
    def validate_description(cls, v: str | None) -> str | None:
        if v is not None and len(v) > 10000:
            raise ValueError("Description must be 10,000 characters or less")
        return v

    @field_validator("estimated_minutes")
    @classmethod
    def validate_estimated_minutes(cls, v: int | None) -> int | None:
        if v is not None and (v < 0 or v > 9999):
            raise ValueError("Estimated minutes must be between 0 and 9999")
        return v


class InstallPathRequest(BaseModel):
    """ADR-014 §8.5: install a purchased learning path from its listing.

    R123[H1]: manual license grants carry NO listing_id — product_id is the
    alternative handle so manually-granted paths are redeemable too. Exactly
    one of the two must be provided."""

    listing_id: str | None = Field(default=None, min_length=26, max_length=26)
    product_id: str | None = Field(default=None, min_length=26, max_length=26)

    @model_validator(mode="after")
    def _one_of(self) -> "InstallPathRequest":
        if bool(self.listing_id) == bool(self.product_id):
            raise ValueError("Provide exactly one of listing_id or product_id")
        return self


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

    @field_validator("description")
    @classmethod
    def validate_description(cls, v: str | None) -> str | None:
        if v is not None and len(v) > 10000:
            raise ValueError("Description must be 10,000 characters or less")
        return v

    @field_validator("estimated_minutes")
    @classmethod
    def validate_estimated_minutes(cls, v: int | None) -> int | None:
        if v is not None and (v < 0 or v > 9999):
            raise ValueError("Estimated minutes must be between 0 and 9999")
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
    item_type: str  # skill / project / section / workflow_pack
    skill_id: str | None = None
    project_id: str | None = None
    section_title: str | None = None
    workflow_pack_id: str | None = Field(default=None, max_length=26)
    sort_order: int = 0
    required: bool = True
    unlock_rule: str = "previous_required"

    @field_validator("item_type")
    @classmethod
    def validate_item_type(cls, v: str) -> str:
        valid = {"skill", "project", "section", "workflow_pack"}
        if v.lower() not in valid:
            raise ValueError(f"item_type must be one of: {', '.join(sorted(valid))}")
        return v

    @field_validator("section_title")
    @classmethod
    def validate_section_title(cls, v: str | None) -> str | None:
        if v is not None and len(v) > 200:
            raise ValueError("Section title must be 200 characters or less")
        return v

    @field_validator("unlock_rule")
    @classmethod
    def validate_unlock_rule(cls, v: str) -> str:
        if len(v) > 30:
            raise ValueError("Unlock rule must be 30 characters or less")
        return v

    @model_validator(mode="after")
    def validate_references(self) -> "AddPathItemRequest":
        t = self.item_type.lower()
        if t == "skill" and not self.skill_id:
            raise ValueError("skill_id is required for skill items")
        if t == "project" and not self.project_id:
            raise ValueError("project_id is required for project items")
        if t == "section" and not self.section_title:
            raise ValueError("section_title is required for section items")
        if t == "workflow_pack" and not self.workflow_pack_id:
            raise ValueError("workflow_pack_id is required for workflow_pack items")
        return self


class PathItemResponse(BaseModel):
    id: str
    path_id: str
    item_type: str
    skill_id: str | None
    project_id: str | None
    section_title: str | None
    workflow_pack_id: str | None = None
    sort_order: int
    required: bool
    unlock_rule: str

    model_config = {"from_attributes": True}


class AssignPathRequest(BaseModel):
    path_id: str


class CohortPathAssignmentResponse(BaseModel):
    cohort_id: str
    path_id: str
    path_name: str | None = None
    assigned_at: datetime
