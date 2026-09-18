"""Pydantic schemas for opportunity bookmarks (N13)."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class BookmarkRequest(BaseModel):
    notes: str | None = Field(None, max_length=500)


class BookmarkResponse(BaseModel):
    id: str
    user_id: str
    opportunity_id: str
    notes: str | None
    created_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)
