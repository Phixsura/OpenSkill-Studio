"""Pydantic schemas for pack reviews."""

from datetime import datetime

from pydantic import BaseModel, Field, field_validator


class CreateReviewRequest(BaseModel):
    rating: int = Field(..., ge=1, le=5)
    title: str | None = None
    body: str | None = None

    @field_validator("title")
    @classmethod
    def validate_title(cls, v: str | None) -> str | None:
        if v is not None:
            v = v.strip()
            if len(v) > 200:
                raise ValueError("Title must be 200 characters or less")
            if len(v) == 0:
                return None
        return v

    @field_validator("body")
    @classmethod
    def validate_body(cls, v: str | None) -> str | None:
        if v is not None:
            v = v.strip()
            if len(v) > 5000:
                raise ValueError("Body must be 5000 characters or less")
            if len(v) == 0:
                return None
        return v


class ReviewResponse(BaseModel):
    id: str
    pack_id: str
    user_id: str
    rating: int
    title: str | None
    body: str | None
    created_at: datetime

    model_config = {"from_attributes": True}


class ReviewStatsResponse(BaseModel):
    average_rating: float | None
    review_count: int
