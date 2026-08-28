"""Pydantic schemas for skill pack management."""

from datetime import datetime

from pydantic import BaseModel, field_validator

from app.schemas.base import reject_deep_json

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

    @field_validator("description")
    @classmethod
    def validate_description(cls, v: str | None) -> str | None:
        if v is not None and len(v) > 10000:
            raise ValueError("Description must be 10000 characters or less")
        return v

    @field_validator("scenario_tags", "tool_tags", "capability_tags")
    @classmethod
    def validate_tags(cls, v: list[str]) -> list[str]:
        v = [t.strip() for t in v if t.strip()]
        if len(v) > 50:
            raise ValueError("Maximum 50 tags allowed")
        for tag in v:
            if len(tag) > 100:
                raise ValueError("Each tag must be 100 characters or less")
        return v

    @field_validator("learning_outcomes")
    @classmethod
    def validate_learning_outcomes(cls, v: list[str]) -> list[str]:
        if len(v) > 20:
            raise ValueError("Maximum 20 learning outcomes allowed")
        for outcome in v:
            if len(outcome) > 500:
                raise ValueError("Each learning outcome must be 500 characters or less")
        return v

    @field_validator("estimated_minutes")
    @classmethod
    def validate_estimated_minutes(cls, v: int | None) -> int | None:
        if v is not None and (v < 0 or v > 9999):
            raise ValueError("Estimated minutes must be between 0 and 9999")
        return v

    @field_validator("language")
    @classmethod
    def validate_language(cls, v: str) -> str:
        if len(v) > 10:
            raise ValueError("Language code must be 10 characters or less")
        return v

    @field_validator("provenance")
    @classmethod
    def validate_provenance_size(cls, v: dict | None) -> dict | None:
        if v is not None and len(str(v)) > 20000:
            raise ValueError("Provenance data too large (max 20,000 chars)")
        return reject_deep_json(v, "provenance")


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

    @field_validator("summary")
    @classmethod
    def validate_summary(cls, v: str | None) -> str | None:
        if v is not None and len(v) > 500:
            raise ValueError("Summary must be 500 characters or less")
        return v

    @field_validator("description")
    @classmethod
    def validate_description(cls, v: str | None) -> str | None:
        if v is not None and len(v) > 10000:
            raise ValueError("Description must be 10000 characters or less")
        return v

    @field_validator("difficulty")
    @classmethod
    def validate_difficulty(cls, v: str | None) -> str | None:
        if v is not None:
            valid = {"beginner", "intermediate", "advanced", "expert"}
            if v not in valid:
                raise ValueError(f"Difficulty must be one of: {', '.join(sorted(valid))}")
        return v

    @field_validator("estimated_minutes")
    @classmethod
    def validate_estimated_minutes(cls, v: int | None) -> int | None:
        if v is not None and (v < 0 or v > 9999):
            raise ValueError("Estimated minutes must be between 0 and 9999")
        return v

    @field_validator("scenario_tags", "tool_tags", "capability_tags")
    @classmethod
    def validate_tags(cls, v: list[str] | None) -> list[str] | None:
        if v is not None:
            v = [t.strip() for t in v if t.strip()]
            if len(v) > 50:
                raise ValueError("Maximum 50 tags allowed")
            for tag in v:
                if len(tag) > 100:
                    raise ValueError("Each tag must be 100 characters or less")
        return v

    @field_validator("learning_outcomes")
    @classmethod
    def validate_learning_outcomes(cls, v: list[str] | None) -> list[str] | None:
        if v is not None:
            if len(v) > 20:
                raise ValueError("Maximum 20 learning outcomes allowed")
            for outcome in v:
                if len(outcome) > 500:
                    raise ValueError("Each learning outcome must be 500 characters or less")
        return v

    @field_validator("language")
    @classmethod
    def validate_language(cls, v: str | None) -> str | None:
        if v is not None and len(v) > 10:
            raise ValueError("Language code must be 10 characters or less")
        return v

    @field_validator("provenance")
    @classmethod
    def validate_provenance_size(cls, v: dict | None) -> dict | None:
        if v is not None and len(str(v)) > 20000:
            raise ValueError("Provenance data too large (max 20,000 chars)")
        return reject_deep_json(v, "provenance")


class RejectPackRequest(BaseModel):
    reason: str | None = None

    @field_validator("reason")
    @classmethod
    def validate_reason(cls, v: str | None) -> str | None:
        if v is not None and len(v) > 500:
            raise ValueError("Reason must be 500 characters or less")
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
    review_count: int = 0
    average_rating: float | None = None
    review_status: str | None = None
    rejection_reason: str | None = None
    quality_score: int | None = None
    badges: list[str] = []
    sharing_enabled: bool = False
    provenance: dict
    created_by: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class PublicSkillPackResponse(BaseModel):
    """Anonymous registry card/detail — internal moderation + ownership fields
    are OMITTED. SkillPackResponse (the authenticated org-scoped shape) leaked
    rejection_reason (the moderator's PRIVATE review note), review_status,
    owner_org_id, and created_by to unauthenticated /registry callers (R71).
    The public registry serves only discovery metadata."""

    id: str
    name: str
    slug: str
    description: str | None = None
    summary: str | None = None
    visibility: str
    language: str
    difficulty: str | None = None
    estimated_minutes: int | None = None
    learning_outcomes: list = []
    scenario_tags: list = []
    tool_tags: list = []
    capability_tags: list = []
    install_count: int = 0
    review_count: int = 0
    average_rating: float | None = None
    quality_score: int | None = None
    badges: list[str] = []
    provenance: dict = {}
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# ── Pack Contents ────────────────────────────────────────


class AddSkillToPackRequest(BaseModel):
    skill_id: str
    sort_order: int = 0

    @field_validator("sort_order")
    @classmethod
    def validate_sort_order(cls, v: int) -> int:
        if v < 0 or v > 100000:
            raise ValueError("sort_order must be between 0 and 100,000")
        return v


class AddTemplateToPackRequest(BaseModel):
    template_id: str
    sort_order: int = 0

    @field_validator("sort_order")
    @classmethod
    def validate_sort_order(cls, v: int) -> int:
        if v < 0 or v > 100000:
            raise ValueError("sort_order must be between 0 and 100,000")
        return v


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

    @field_validator("changelog")
    @classmethod
    def validate_changelog(cls, v: str | None) -> str | None:
        if v is not None and len(v) > 5000:
            raise ValueError("Changelog must be 5000 characters or less")
        return v

    @field_validator("version")
    @classmethod
    def validate_version(cls, v: str) -> str:
        import re

        v = v.strip()
        if not v:
            raise ValueError("Version is required")
        if len(v) > 50:
            raise ValueError("Version must be 50 characters or less")
        if not re.match(r"^\d+\.\d+\.\d+(-[a-zA-Z0-9.]+)?$", v):
            raise ValueError("Version must be in semver format X.Y.Z or X.Y.Z-prerelease")
        # Prevent integer overflow in _parse_semver
        base = v.partition("-")[0]
        if any(int(p) > 999 for p in base.split(".")):
            raise ValueError("Version components must be 999 or less")
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


class PublicReleaseResponse(BaseModel):
    """Anonymous registry release entry — OMITS released_by (the publisher's
    user id, an internal identifier the anon /registry/packs/{id}/releases
    endpoint has no business exposing to the world — R72). Mirrors the
    workflow twin PublicWorkflowReleaseResponse, which already omits it."""

    id: str
    pack_id: str
    version: str
    changelog: str | None = None
    checksum: str
    component_count: int
    released_at: datetime

    model_config = {"from_attributes": True}
