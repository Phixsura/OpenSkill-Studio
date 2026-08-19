"""Pydantic schemas for skill pack management."""

from datetime import datetime

from pydantic import BaseModel, field_validator

# ── Pack CRUD ────────────────────────────────────────────


class CreateSkillPackRequest(BaseModel):
    name: str
    description: str | None = None
    summary: str | None = None
    visibility: str = "private"
    language: str = "en"
    difficulty: str | None = None
    estimated_minutes: int | None = None
    learning_outcomes: list[str] = []
    scenario_tags: list[str] = []
    tool_tags: list[str] = []
    capability_tags: list[str] = []
    provenance: dict | None = None

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        v = v.strip()
        if len(v) < 2 or len(v) > 200:
            raise ValueError("Name must be 2-200 characters")
        return v

    @field_validator("summary")
    @classmethod
    def validate_summary(cls, v: str | None) -> str | None:
        if v is not None and len(v) > 500:
            raise ValueError("Summary must be 500 characters or less")
        return v

    @field_validator("visibility")
    @classmethod
    def validate_visibility(cls, v: str) -> str:
        valid = {"private", "unlisted", "public"}
        if v not in valid:
            raise ValueError(f"Visibility must be one of: {', '.join(sorted(valid))}")
        return v

    @field_validator("difficulty")
    @classmethod
    def validate_difficulty(cls, v: str | None) -> str | None:
        if v is not None:
            valid = {"beginner", "intermediate", "advanced", "expert"}
            if v not in valid:
                raise ValueError(f"Difficulty must be one of: {', '.join(sorted(valid))}")
        return v


class UpdateSkillPackRequest(BaseModel):
    name: str | None = None
    description: str | None = None
    summary: str | None = None
    visibility: str | None = None
    language: str | None = None
    difficulty: str | None = None
    estimated_minutes: int | None = None
    learning_outcomes: list[str] | None = None
    scenario_tags: list[str] | None = None
    tool_tags: list[str] | None = None
    capability_tags: list[str] | None = None
    provenance: dict | None = None

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str | None) -> str | None:
        if v is not None:
            v = v.strip()
            if len(v) < 2 or len(v) > 200:
                raise ValueError("Name must be 2-200 characters")
        return v

    @field_validator("visibility")
    @classmethod
    def validate_visibility(cls, v: str | None) -> str | None:
        if v is not None:
            valid = {"private", "unlisted", "public"}
            if v not in valid:
                raise ValueError(f"Visibility must be one of: {', '.join(sorted(valid))}")
        return v


class SkillPackResponse(BaseModel):
    id: str
    owner_org_id: str
    name: str
    slug: str
    description: str | None
    summary: str | None
    status: str
    visibility: str
    language: str
    difficulty: str | None
    estimated_minutes: int | None
    learning_outcomes: list
    scenario_tags: list
    tool_tags: list
    capability_tags: list
    install_count: int
    provenance: dict
    created_by: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# ── Pack Contents ────────────────────────────────────────


class AddSkillToPackRequest(BaseModel):
    skill_id: str
    sort_order: int = 0


class AddTemplateToPackRequest(BaseModel):
    template_id: str
    sort_order: int = 0


class PackSkillResponse(BaseModel):
    pack_id: str
    skill_id: str
    skill_name: str | None = None
    sort_order: int

    model_config = {"from_attributes": True}


class PackTemplateResponse(BaseModel):
    pack_id: str
    template_id: str
    template_name: str | None = None
    sort_order: int

    model_config = {"from_attributes": True}


# ── Releases ─────────────────────────────────────────────


class PublishReleaseRequest(BaseModel):
    version: str
    changelog: str | None = None

    @field_validator("version")
    @classmethod
    def validate_version(cls, v: str) -> str:
        v = v.strip()
        if len(v) > 20:
            raise ValueError("Version must be 20 characters or less")
        return v


class ReleaseResponse(BaseModel):
    id: str
    pack_id: str
    version: str
    changelog: str | None
    checksum: str
    component_count: int
    released_by: str
    released_at: datetime

    model_config = {"from_attributes": True}


class ReleaseDetailResponse(ReleaseResponse):
    manifest: dict

    model_config = {"from_attributes": True}
