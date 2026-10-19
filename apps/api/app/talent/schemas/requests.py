"""Pydantic request models for talent API endpoints that previously accepted raw dict."""

from pydantic import BaseModel, Field


class CreateApplicationBody(BaseModel):
    opportunity_id: str = Field(..., min_length=1, max_length=26)


class CreateBookmarkBody(BaseModel):
    entity_type: str = Field(default="opportunity", max_length=50)
    entity_id: str | None = Field(default=None, max_length=26)
    opportunity_id: str | None = Field(default=None, max_length=26)


class CreateSavedSearchBody(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    query: dict = Field(default_factory=dict)
    org_id: str | None = Field(default=None, max_length=26)


class ValidateCustomQuestionsBody(BaseModel):
    questions: list[dict] = Field(default_factory=list, max_length=50)


class AutoScreenBody(BaseModel):
    criteria: dict = Field(default_factory=dict)


class SendMessageBody(BaseModel):
    content: str = Field(..., min_length=1, max_length=10000)
    message_type: str = Field(default="text", max_length=50)


class CreatePortfolioItemBody(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: str = Field(default="", max_length=5000)
    item_type: str = Field(default="project", max_length=50)
    url: str | None = Field(default=None, max_length=2000)
    media_urls: list[str] = Field(default_factory=list, max_length=20)


class CreateOfferBody(BaseModel):
    application_id: str = Field(..., min_length=1, max_length=26)
    title: str = Field(..., min_length=1, max_length=200)
    compensation: dict = Field(default_factory=dict)
    start_date: str | None = Field(default=None, max_length=20)
    expires_at: str | None = Field(default=None, max_length=30)


class WebhookBody(BaseModel):
    url: str = Field(..., min_length=1, max_length=2000)
    events: list[str] = Field(default_factory=list, max_length=50)
    secret: str | None = Field(default=None, max_length=200)


class SuccessionPlanBody(BaseModel):
    role_title: str = Field(..., min_length=1, max_length=200)
    org_id: str = Field(..., min_length=1, max_length=26)
    required_capabilities: list[str] = Field(default_factory=list, max_length=50)
    timeline_months: int = Field(default=12, ge=1, le=120)


class AnalyticsBody(BaseModel):
    """Generic analytics request body — accepts flexible parameters."""

    model_config = {"extra": "allow"}  # Allow additional fields for analytics queries

    def get(self, key: str, default=None):
        """R492 (found by the OpenAPI fuzz sweep): dozens of handlers call
        `body.get(...)` on this model — BaseModel has no `.get`, so every
        such route 500'd AttributeError on ANY request (production-dead,
        not merely hostile-input fragile). Dict-style access over declared
        + extra fields revives all of them at the one shared point.

        R508 (review finding #5): NEVER a raw getattr fallback — a key that
        collides with a BaseModel attribute ("copy", "schema", "json",
        "model_fields") must return the default, not a bound method."""
        extra = self.model_extra or {}
        if key in extra:
            return extra[key]
        if key in type(self).model_fields:
            value = getattr(self, key)
            return default if value is None else value
        return default
