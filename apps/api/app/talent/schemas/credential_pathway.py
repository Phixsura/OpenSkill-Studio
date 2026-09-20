"""Pydantic schemas for credential pathway endpoints."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator


class CreatePathwayRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    description: str | None = Field(None, max_length=5000)
    pathway_credential_type: str = Field(..., min_length=1, max_length=100)
    prerequisite_credential_types: list[str] = Field(..., min_length=2, max_length=20)
    prerequisite_count: int | None = Field(None, ge=1)
    auto_issue: bool = True

    @field_validator("prerequisite_credential_types")
    @classmethod
    def _no_empty_types(cls, v: list[str]) -> list[str]:
        if any(not t.strip() for t in v):
            raise ValueError("Prerequisite credential types must not be empty strings")
        return v


class UpdatePathwayRequest(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=200)
    description: str | None = Field(None, max_length=500)
    prerequisite_count: int | None = Field(None, ge=1)
    auto_issue: bool | None = None
    status: str | None = Field(None, max_length=500)

    @field_validator("status")
    @classmethod
    def _valid_status(cls, v: str | None) -> str | None:
        if v is not None and v not in ("active", "archived"):
            raise ValueError("status must be 'active' or 'archived'")
        return v


class PathwayResponse(BaseModel):
    id: str
    org_id: str
    name: str
    description: str | None
    pathway_credential_type: str
    prerequisite_credential_types: list[str]
    prerequisite_count: int
    auto_issue: bool
    status: str
    created_by: str | None
    created_at: datetime | None = None
    updated_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)


class PathwayProgressResponse(BaseModel):
    completed: bool
    pathway_id: str
    pathway_name: str
    target_credential_type: str
    required_count: int
    earned_count: int
    earned_credentials: list[dict]
    missing_credential_types: list[str]
