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
