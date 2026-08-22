"""Pydantic schemas for the personal overview / dashboard landing."""

from datetime import datetime

from pydantic import BaseModel


class DraftSummary(BaseModel):
    submission_id: str
    project_id: str
    org_id: str
    project_title: str


class ReviewReceived(BaseModel):
    review_id: str
    score: int | None
    created_at: datetime
    project_id: str
    org_id: str
    submission_id: str
    project_title: str


class OverviewResponse(BaseModel):
    drafts: list[DraftSummary]
    peer_assessments_pending: int
    reviews_received: list[ReviewReceived]
    pending_reviews_to_grade: int
