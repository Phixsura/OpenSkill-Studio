"""Pydantic schemas for Skill Passport endpoints."""

from datetime import datetime

from pydantic import BaseModel, Field


class UpdatePassportRequest(BaseModel):
    default_visibility: str | None = None
    visible_fields: list[str] | None = None
    preferred_opportunity_types: list[str] | None = None
    availability_status: str | None = None
    availability_note: str | None = Field(None, max_length=500)
    discoverable: bool | None = None
    discoverable_to: list[str] | None = None


class PassportResponse(BaseModel):
    user_id: str
    default_visibility: str
    discoverable: bool
    availability_status: str | None
    availability_note: str | None
    preferred_opportunity_types: list[str]
    visible_fields: list[str]
    capabilities: list[dict] | None = None

    model_config = {"from_attributes": True}


class CreateSnapshotRequest(BaseModel):
    included_fields: list[str] | None = None
    expires_at: datetime | None = None


class SnapshotResponse(BaseModel):
    id: str
    user_id: str
    share_token: str
    checksum: str
    included_fields: list[str]
    issued_at: datetime
    expires_at: datetime | None
    status: str

    model_config = {"from_attributes": True}


class SnapshotVerifyResponse(BaseModel):
    status: str
    payload: dict | None = None
    checksum: str | None = None
    issued_at: str | None = None
    expires_at: str | None = None
    revoked: bool | None = None
    expired: bool | None = None
