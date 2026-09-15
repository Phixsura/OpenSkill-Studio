"""Pydantic schemas for career goal endpoints."""

from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field


class CreateGoalRequest(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: str | None = Field(None, max_length=5000)
    target_role: str | None = Field(None, max_length=200)
    target_capabilities: list[dict] | None = None
    target_date: date | None = None


class UpdateGoalRequest(BaseModel):
    title: str | None = Field(None, min_length=1, max_length=200)
    description: str | None = None
    target_role: str | None = None
    target_capabilities: list[dict] | None = None
    target_date: date | None = None


class GoalResponse(BaseModel):
    id: str
    user_id: str
    title: str
    description: str | None
    target_role: str | None
    target_capabilities: list[dict]
    target_date: date | None
    status: str
    completed_at: datetime | None
    created_at: datetime | None = None
    updated_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)


class GoalProgressResponse(BaseModel):
    goal_id: str
    title: str
    overall_progress: float
    target_date: date | None = None
    days_remaining: int | None
    capabilities: list[dict]
