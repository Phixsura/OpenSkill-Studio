"""Pydantic schemas for AI System Inventory (ADR-017 Part A)."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, field_validator

from app.schemas.base import reject_ctrl_json, reject_ctrl_str, reject_deep_json

# Valid values for client-side validation messages
VALID_SYSTEM_TYPES = {"workflow_pack", "developer_app", "provider_binding", "evaluation_pipeline", "skill_pack", "custom"}
VALID_LIFECYCLES = {"draft", "intake", "under_review", "approved", "deployed", "monitoring", "paused", "deprecated", "retired"}
VALID_USE_TYPES = {"intended", "prohibited"}
VALID_LINKED_ENTITY_TYPES = {"workflow_pack", "developer_app", "provider_connection", "evaluation_pipeline", "skill_pack"}


# ── System schemas ───────────────────────────────────────────────────


class CreateSystemRequest(BaseModel):
    name: str
    system_type: str
    slug: str | None = None
    description: str | None = None
    linked_entity_type: str | None = None
    linked_entity_id: str | None = None
    tags: list[str] | None = None
    metadata_: dict | None = None

    @field_validator("name")
    @classmethod
    def validate_name(cls, v):
        v = reject_ctrl_str(v, "name")
        if not v or len(v.strip()) == 0:
            raise ValueError("name must not be empty")
        if len(v) > 200:
            raise ValueError("name must be 200 characters or fewer")
        return v.strip()

    @field_validator("system_type")
    @classmethod
    def validate_system_type(cls, v):
        if v not in VALID_SYSTEM_TYPES:
            raise ValueError(f"system_type must be one of: {', '.join(sorted(VALID_SYSTEM_TYPES))}")
        return v

    @field_validator("slug")
    @classmethod
    def validate_slug(cls, v):
        if v is not None:
            v = reject_ctrl_str(v, "slug")
            if len(v) > 100:
                raise ValueError("slug must be 100 characters or fewer")
        return v

    @field_validator("description")
    @classmethod
    def validate_description(cls, v):
        if v is not None:
            v = reject_ctrl_str(v, "description")
        return v

    @field_validator("tags")
    @classmethod
    def validate_tags(cls, v):
        if v is not None:
            reject_ctrl_json(v, "tags")
            reject_deep_json(v, "tags", limit=4)
            if len(v) > 50:
                raise ValueError("tags may contain at most 50 items")
        return v

    @field_validator("metadata_")
    @classmethod
    def validate_metadata(cls, v):
        if v is not None:
            reject_ctrl_json(v, "metadata")
            reject_deep_json(v, "metadata")
        return v

    @field_validator("linked_entity_type")
    @classmethod
    def validate_linked_entity_type(cls, v):
        if v is not None and v not in VALID_LINKED_ENTITY_TYPES:
            raise ValueError(f"linked_entity_type must be one of: {', '.join(sorted(VALID_LINKED_ENTITY_TYPES))}")
        return v


class UpdateSystemRequest(BaseModel):
    name: str | None = None
    description: str | None = None
    system_type: str | None = None
    tags: list[str] | None = None
    metadata_: dict | None = None

    @field_validator("name")
    @classmethod
    def validate_name(cls, v):
        if v is not None:
            v = reject_ctrl_str(v, "name")
            if len(v.strip()) == 0:
                raise ValueError("name must not be empty")
            if len(v) > 200:
                raise ValueError("name must be 200 characters or fewer")
            return v.strip()
        return v

    @field_validator("system_type")
    @classmethod
    def validate_system_type(cls, v):
        if v is not None and v not in VALID_SYSTEM_TYPES:
            raise ValueError(f"system_type must be one of: {', '.join(sorted(VALID_SYSTEM_TYPES))}")
        return v

    @field_validator("description")
    @classmethod
    def validate_description(cls, v):
        if v is not None:
            v = reject_ctrl_str(v, "description")
        return v

    @field_validator("tags")
    @classmethod
    def validate_tags(cls, v):
        if v is not None:
            reject_ctrl_json(v, "tags")
            reject_deep_json(v, "tags", limit=4)
        return v

    @field_validator("metadata_")
    @classmethod
    def validate_metadata(cls, v):
        if v is not None:
            reject_ctrl_json(v, "metadata")
            reject_deep_json(v, "metadata")
        return v


class ChangeLifecycleRequest(BaseModel):
    lifecycle: str
    reason: str | None = None

    @field_validator("lifecycle")
    @classmethod
    def validate_lifecycle(cls, v):
        if v not in VALID_LIFECYCLES:
            raise ValueError(f"lifecycle must be one of: {', '.join(sorted(VALID_LIFECYCLES))}")
        return v

    @field_validator("reason")
    @classmethod
    def validate_reason(cls, v):
        if v is not None:
            v = reject_ctrl_str(v, "reason")
        return v


class LinkEntityRequest(BaseModel):
    entity_type: str
    entity_id: str

    @field_validator("entity_type")
    @classmethod
    def validate_entity_type(cls, v):
        if v not in VALID_LINKED_ENTITY_TYPES:
            raise ValueError(f"entity_type must be one of: {', '.join(sorted(VALID_LINKED_ENTITY_TYPES))}")
        return v


class SystemResponse(BaseModel):
    id: str
    org_id: str
    name: str
    slug: str
    description: str | None
    system_type: str
    lifecycle: str
    risk_tier: str | None
    owner_user_id: str
    linked_entity_type: str | None
    linked_entity_id: str | None
    tags: list
    metadata_: dict | None = None
    version: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class SystemSummaryResponse(BaseModel):
    id: str
    name: str
    slug: str
    system_type: str
    lifecycle: str
    risk_tier: str | None
    owner_user_id: str
    version: int
    created_at: datetime

    model_config = {"from_attributes": True}


# ── Use Case schemas ─────────────────────────────────────────────────


class CreateUseCaseRequest(BaseModel):
    use_type: str
    title: str
    description: str
    affected_groups: list[str] | None = None
    data_classes: list[str] | None = None
    deployment_contexts: list[str] | None = None
    regions: list[str] | None = None

    @field_validator("use_type")
    @classmethod
    def validate_use_type(cls, v):
        if v not in VALID_USE_TYPES:
            raise ValueError(f"use_type must be one of: {', '.join(sorted(VALID_USE_TYPES))}")
        return v

    @field_validator("title")
    @classmethod
    def validate_title(cls, v):
        v = reject_ctrl_str(v, "title")
        if not v or len(v.strip()) == 0:
            raise ValueError("title must not be empty")
        if len(v) > 200:
            raise ValueError("title must be 200 characters or fewer")
        return v.strip()

    @field_validator("description")
    @classmethod
    def validate_description(cls, v):
        v = reject_ctrl_str(v, "description")
        if not v or len(v.strip()) == 0:
            raise ValueError("description must not be empty")
        return v

    @field_validator("affected_groups", "data_classes", "deployment_contexts", "regions")
    @classmethod
    def validate_list_fields(cls, v, info):
        if v is not None:
            reject_ctrl_json(v, info.field_name)
            reject_deep_json(v, info.field_name, limit=4)
        return v


class UpdateUseCaseRequest(BaseModel):
    title: str | None = None
    description: str | None = None
    affected_groups: list[str] | None = None
    data_classes: list[str] | None = None
    deployment_contexts: list[str] | None = None
    regions: list[str] | None = None

    @field_validator("title")
    @classmethod
    def validate_title(cls, v):
        if v is not None:
            v = reject_ctrl_str(v, "title")
            if len(v.strip()) == 0:
                raise ValueError("title must not be empty")
            if len(v) > 200:
                raise ValueError("title must be 200 characters or fewer")
            return v.strip()
        return v

    @field_validator("description")
    @classmethod
    def validate_description(cls, v):
        if v is not None:
            v = reject_ctrl_str(v, "description")
        return v

    @field_validator("affected_groups", "data_classes", "deployment_contexts", "regions")
    @classmethod
    def validate_list_fields(cls, v, info):
        if v is not None:
            reject_ctrl_json(v, info.field_name)
            reject_deep_json(v, info.field_name, limit=4)
        return v


class UseCaseResponse(BaseModel):
    id: str
    system_id: str
    use_type: str
    title: str
    description: str
    affected_groups: list
    data_classes: list
    deployment_contexts: list
    regions: list
    created_by: str | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
