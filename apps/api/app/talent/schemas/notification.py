"""Pydantic schemas for talent notifications."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class NotificationResponse(BaseModel):
    id: str
    user_id: str
    event_type: str
    title: str
    message: str
    extra: dict = Field(default_factory=dict, validation_alias="extra")
    read_at: datetime | None = None
    created_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)


class NotificationPreferenceResponse(BaseModel):
    event_type: str
    channel: str
    enabled: bool


class UpdatePreferencesRequest(BaseModel):
    preferences: list[dict] = Field(
        ...,
        min_length=1,
        max_length=20,
        description="List of {event_type, enabled, channel?} dicts",
    )


class UnreadCountResponse(BaseModel):
    count: int
