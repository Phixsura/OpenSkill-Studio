"""Pydantic schemas for pack reviews."""

from datetime import datetime

from pydantic import BaseModel, Field, field_validator, model_validator


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

    @model_validator(mode="after")
    def low_rating_requires_body(self) -> "CreateReviewRequest":
        """Ratings of 1 or 2 require a body of at least 20 characters."""
        if self.rating <= 2 and (self.body is None or len(self.body) < 20):
            raise ValueError(
                "Reviews with a rating of 2 or below must include a body of at least 20 characters"
            )
        return self


class UpdateReviewRequest(BaseModel):
    rating: int | None = Field(default=None, ge=1, le=5)
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

    @model_validator(mode="after")
    def low_rating_requires_body(self) -> "UpdateReviewRequest":
        """If rating is being set to 1 or 2, body must be at least 20 characters."""
        if (
            self.rating is not None
            and self.rating <= 2
            and (self.body is None or len(self.body) < 20)
        ):
            raise ValueError(
                "Reviews with a rating of 2 or below must include a body of at least 20 characters"
            )
        return self


class ReplyRequest(BaseModel):
    reply_text: str = Field(..., min_length=1, max_length=1000)

    @field_validator("reply_text")
    @classmethod
    def validate_reply_text(cls, v: str) -> str:
        v = v.strip()
        if len(v) == 0:
            raise ValueError("Reply text cannot be empty")
        if len(v) > 1000:
            raise ValueError("Reply text must be 1000 characters or less")
        return v


class ReviewResponse(BaseModel):
    id: str
    pack_id: str
    user_id: str
    rating: int
    title: str | None
    body: str | None
    helpful_count: int
    reply_text: str | None
    reply_at: datetime | None
    created_at: datetime
    user_display_name: str | None = None

    model_config = {"from_attributes": True}


class ReviewStatsResponse(BaseModel):
    average_rating: float | None
    review_count: int


class RatingDistributionResponse(BaseModel):
    average: float | None
    total: int
    distribution: dict[int, int]
