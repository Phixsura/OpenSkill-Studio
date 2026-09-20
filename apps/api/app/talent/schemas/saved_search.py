"""Pydantic schemas for saved search endpoints."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.talent.models.saved_search import NOTIFY_FREQUENCIES, SEARCH_TYPES


class CreateSavedSearchRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    description: str | None = Field(None, max_length=2000)
    search_type: str | None = Field(..., max_length=500)
    search_criteria: dict = Field(default_factory=dict)
    notify_frequency: str | None = Field("never", max_length=500)

    @field_validator("search_type")
    @classmethod
    def _validate_search_type(cls, v: str) -> str:
        if v not in SEARCH_TYPES:
            raise ValueError(f"search_type must be one of {sorted(SEARCH_TYPES)}")
        return v

    @field_validator("notify_frequency")
    @classmethod
    def _validate_notify_frequency(cls, v: str) -> str:
        if v not in NOTIFY_FREQUENCIES:
            raise ValueError(f"notify_frequency must be one of {sorted(NOTIFY_FREQUENCIES)}")
        return v


class UpdateSavedSearchRequest(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=200)
    description: str | None = Field(None, max_length=500)
    search_criteria: dict | None = Field(None)
    notify_frequency: str | None = Field(None, max_length=500)

    @field_validator("notify_frequency")
    @classmethod
    def _validate_notify_frequency(cls, v: str | None) -> str | None:
        if v is not None and v not in NOTIFY_FREQUENCIES:
            raise ValueError(f"notify_frequency must be one of {sorted(NOTIFY_FREQUENCIES)}")
        return v


class SavedSearchResponse(BaseModel):
    id: str
    org_id: str
    name: str
    description: str | None
    search_type: str
    search_criteria: dict
    notify_frequency: str
    last_run_at: datetime | None
    result_count: int
    created_by: str
    created_at: datetime | None = None
    updated_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)


class SavedSearchRunResponse(BaseModel):
    search_id: str
    results: list[dict]
    result_count: int
    run_at: datetime
