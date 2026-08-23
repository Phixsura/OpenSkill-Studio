"""Schemas for workflow packs, releases, installations (ADR-010)."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, field_validator


class CreateWorkflowPackRequest(BaseModel):
    name: str
    summary: str | None = None
    description: str | None = None
    workflow_type: str = "production"
    scenario_tags: list[str] = []
    tool_tags: list[str] = []
    difficulty: str | None = None
    language: str = "en"
    provenance: dict = {}

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        v = v.strip()
        if not v or len(v) > 200:
            raise ValueError("Name must be 1-200 characters")
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
        if v is not None and len(v) > 20000:
            raise ValueError("Description must be 20,000 characters or less")
        return v

    @field_validator("workflow_type")
    @classmethod
    def validate_workflow_type(cls, v: str) -> str:
        if v not in ("production", "pipeline", "review"):
            raise ValueError("Workflow type must be production, pipeline, or review")
        return v

    @field_validator("scenario_tags", "tool_tags")
    @classmethod
    def validate_tags(cls, v: list) -> list:
        if len(v) > 20:
            raise ValueError("Maximum 20 tags")
        for tag in v:
            if not isinstance(tag, str) or not tag.strip() or len(tag) > 50:
                raise ValueError("Tags must be non-empty strings of max 50 chars")
        return [t.strip() for t in v]

    @field_validator("difficulty")
    @classmethod
    def validate_difficulty(cls, v: str | None) -> str | None:
        if v is not None and v not in ("beginner", "intermediate", "advanced", "expert"):
            raise ValueError("Invalid difficulty")
        return v

    @field_validator("provenance")
    @classmethod
    def validate_provenance(cls, v: dict) -> dict:
        if len(str(v)) > 20000:
            raise ValueError("Provenance too large (max 20,000 chars)")
        return v


class UpdateWorkflowPackRequest(BaseModel):
    name: str | None = None
    summary: str | None = None
    description: str | None = None
    workflow_type: str | None = None
    visibility: str | None = None
    scenario_tags: list[str] | None = None
    tool_tags: list[str] | None = None
    difficulty: str | None = None
    provenance: dict | None = None

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str | None) -> str | None:
        if v is not None:
            v = v.strip()
            if not v or len(v) > 200:
                raise ValueError("Name must be 1-200 characters")
        return v

    @field_validator("visibility")
    @classmethod
    def validate_visibility(cls, v: str | None) -> str | None:
        if v is not None and v not in ("private", "unlisted", "public"):
            raise ValueError("Visibility must be private, unlisted, or public")
        return v

    @field_validator("workflow_type")
    @classmethod
    def validate_workflow_type(cls, v: str | None) -> str | None:
        if v is not None and v not in ("production", "pipeline", "review"):
            raise ValueError("Workflow type must be production, pipeline, or review")
        return v

    @field_validator("provenance")
    @classmethod
    def validate_provenance(cls, v: dict | None) -> dict | None:
        if v is not None and len(str(v)) > 20000:
            raise ValueError("Provenance too large (max 20,000 chars)")
        return v


class UpdateDefinitionRequest(BaseModel):
    definition: dict

    @field_validator("definition")
    @classmethod
    def validate_definition_size(cls, v: dict) -> dict:
        # Full graph validation happens in the service; this is just a cheap
        # pre-parse bound so oversized payloads fail fast.
        if len(str(v)) > 400000:
            raise ValueError("Definition too large")
        return v


class PublishWorkflowReleaseRequest(BaseModel):
    version: str
    changelog: str | None = None
    dependencies: dict = {}

    @field_validator("version")
    @classmethod
    def validate_version(cls, v: str) -> str:
        import re

        if not re.match(r"^\d+\.\d+\.\d+(-[0-9A-Za-z.-]+)?$", v):
            raise ValueError("Version must be semver (X.Y.Z)")
        return v

    @field_validator("changelog")
    @classmethod
    def validate_changelog(cls, v: str | None) -> str | None:
        if v is not None and len(v) > 10000:
            raise ValueError("Changelog must be 10,000 characters or less")
        return v

    @field_validator("dependencies")
    @classmethod
    def validate_dependencies_size(cls, v: dict) -> dict:
        if len(str(v)) > 10000:
            raise ValueError("Dependencies too large")
        return v


class RejectPackRequest(BaseModel):
    reason: str | None = None

    @field_validator("reason")
    @classmethod
    def validate_reason(cls, v: str | None) -> str | None:
        if v is not None and len(v) > 500:
            raise ValueError("Reason must be 500 characters or less")
        return v


class WorkflowPackResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    owner_org_id: str
    name: str
    slug: str
    summary: str | None = None
    description: str | None = None
    status: str
    visibility: str
    language: str
    workflow_type: str
    scenario_tags: list
    tool_tags: list
    capability_tags: list
    difficulty: str | None = None
    install_count: int
    review_status: str | None = None
    rejection_reason: str | None = None
    provenance: dict
    input_schema: list
    output_schema: list
    definition_updated_at: datetime | None = None
    created_at: datetime
    updated_at: datetime


class WorkflowPackDetailResponse(WorkflowPackResponse):
    """Detail response includes the working definition."""

    definition: dict


class WorkflowReleaseResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    pack_id: str
    version: str
    changelog: str | None = None
    checksum: str
    step_count: int
    deprecated_by: str | None = None
    released_at: datetime


class ValidationErrorItem(BaseModel):
    code: str
    pointer: str
    message: str
    meta: dict | None = None


class ValidateDefinitionResponse(BaseModel):
    valid: bool
    errors: list[ValidationErrorItem]
