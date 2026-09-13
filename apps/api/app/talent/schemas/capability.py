"""Pydantic schemas for capability ontology endpoints."""

from datetime import datetime

from pydantic import BaseModel, Field, field_validator

from app.schemas.base import reject_ctrl_str


class CreateCapabilityRequest(BaseModel):
    canonical_name: str = Field(..., min_length=1, max_length=120)
    category: str = Field(..., min_length=1, max_length=40)
    description: str | None = Field(None, max_length=2000)
    parent_id: str | None = None
    capability_tag_id: str | None = None
    level_definitions: dict | None = None
    decay_config: dict | None = None
    sort_order: int = 0

    @field_validator("canonical_name")
    @classmethod
    def _clean_name(cls, v: str) -> str:
        return reject_ctrl_str(v, "canonical_name")


class UpdateCapabilityRequest(BaseModel):
    canonical_name: str | None = Field(None, min_length=1, max_length=120)
    category: str | None = Field(None, min_length=1, max_length=40)
    description: str | None = Field(None, max_length=2000)
    parent_id: str | None = None
    status: str | None = None
    level_definitions: dict | None = None
    decay_config: dict | None = None
    sort_order: int | None = None


class CapabilityResponse(BaseModel):
    id: str
    canonical_name: str
    slug: str
    description: str | None
    category: str
    parent_id: str | None
    status: str
    merged_into_id: str | None
    capability_tag_id: str | None
    level_definitions: dict | None
    decay_config: dict | None
    sort_order: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class CreateEdgeRequest(BaseModel):
    source_id: str
    target_id: str
    edge_type: str = Field(..., min_length=1, max_length=30)
    metadata: dict | None = None


class EdgeResponse(BaseModel):
    id: str
    source_id: str
    target_id: str
    edge_type: str
    metadata: dict | None = Field(None, validation_alias="extra")
    created_at: datetime

    model_config = {"from_attributes": True, "populate_by_name": True}


class CreateMappingRequest(BaseModel):
    capability_id: str
    source_type: str = Field(..., min_length=1, max_length=30)
    source_id: str
    contribution_weight: float = Field(1.0, ge=0.0, le=1.0)
    evidence_type: str = "primary_instruction"


class MappingResponse(BaseModel):
    id: str
    capability_id: str
    source_type: str
    source_id: str
    contribution_weight: float
    evidence_type: str
    created_at: datetime

    model_config = {"from_attributes": True}


class GraphResponse(BaseModel):
    root_id: str
    nodes: list[dict]
    edges: list[dict]


class MergeCapabilityRequest(BaseModel):
    target_id: str
