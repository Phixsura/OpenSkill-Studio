"""Pydantic schemas for skill endorsements."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class CreateEndorsementRequest(BaseModel):
    capability_id: str
    relationship: str = Field(..., min_length=1, max_length=30)
    message: str | None = Field(None, max_length=500)


class EndorsementResponse(BaseModel):
    id: str
    user_id: str
    endorser_id: str
    capability_id: str
    relationship: str
    message: str | None = None
    status: str
    created_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)


class EndorsementSummaryResponse(BaseModel):
    total: int
    by_capability: dict[str, int]
    by_relationship: dict[str, int]
