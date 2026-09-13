"""Pydantic schemas for employer/opportunity endpoints."""

from datetime import datetime

from pydantic import BaseModel, Field, field_validator

from app.schemas.base import reject_ctrl_json, reject_ctrl_str, reject_nonfinite_json


class CreateEmployerProfileRequest(BaseModel):
    company_size: str | None = Field(None, max_length=30)
    industry: str | None = Field(None, max_length=100)
    website_url: str | None = Field(None, max_length=500)
    logo_url: str | None = Field(None, max_length=500)
    description: str | None = Field(None, max_length=5000)


class EmployerProfileResponse(BaseModel):
    org_id: str
    company_size: str | None
    industry: str | None
    website_url: str | None
    logo_url: str | None
    description: str | None
    verification_status: str
    verified_at: datetime | None
    created_at: datetime | None = None
    updated_at: datetime | None = None

    model_config = {"from_attributes": True}


class CreateOpportunityRequest(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: str | None = Field(None, max_length=10000)
    opportunity_type: str = Field(..., min_length=1, max_length=30)
    location_mode: str | None = Field(None, max_length=20)
    location_text: str | None = Field(None, max_length=200)
    compensation_display: str | None = Field(None, max_length=200)
    required_capabilities: list[dict] = Field(default_factory=list)
    preferred_capabilities: list[dict] = Field(default_factory=list)
    minimum_verification: str | None = None
    portfolio_requirements: str | None = Field(None, max_length=5000)
    application_deadline: datetime | None = None
    openings: int = Field(1, ge=1, le=1000)

    @field_validator("title")
    @classmethod
    def _clean_title(cls, v):
        return reject_ctrl_str(v, "title")

    @field_validator("required_capabilities", "preferred_capabilities")
    @classmethod
    def _clean_caps(cls, v):
        v = reject_ctrl_json(v, "capabilities")
        return reject_nonfinite_json(v, "capabilities")


class UpdateOpportunityRequest(BaseModel):
    title: str | None = Field(None, min_length=1, max_length=200)
    description: str | None = Field(None, max_length=10000)
    opportunity_type: str | None = None
    location_mode: str | None = None
    location_text: str | None = None
    compensation_display: str | None = None
    required_capabilities: list[dict] | None = None
    preferred_capabilities: list[dict] | None = None
    minimum_verification: str | None = None
    portfolio_requirements: str | None = None
    application_deadline: datetime | None = None
    openings: int | None = Field(None, ge=1, le=1000)
    status: str | None = None


class OpportunityResponse(BaseModel):
    id: str
    employer_org_id: str
    title: str
    description: str | None
    opportunity_type: str
    location_mode: str | None
    location_text: str | None
    compensation_display: str | None
    required_capabilities: list[dict]
    preferred_capabilities: list[dict]
    minimum_verification: str | None
    portfolio_requirements: str | None
    application_deadline: datetime | None
    openings: int
    status: str
    created_by: str | None
    created_at: datetime | None = None
    updated_at: datetime | None = None

    model_config = {"from_attributes": True}
