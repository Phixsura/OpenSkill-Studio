"""App Review Workflow — manage app review and approval workflows.

Manages review processes for app submissions:
- Submit apps for review
- Assign reviewers
- Track review status and feedback
- Approve/reject decisions
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from enum import Enum

import structlog

log = structlog.get_logger()


class ReviewStatus(str, Enum):
    PENDING = "pending"
    IN_REVIEW = "in_review"
    APPROVED = "approved"
    REJECTED = "rejected"
    CHANGES_REQUESTED = "changes_requested"


@dataclass
class ReviewSubmission:
    """An app review submission."""

    submission_id: str
    installation_id: str
    app_version: str
    status: ReviewStatus = ReviewStatus.PENDING
    reviewer: str = ""
    feedback: str = ""
    submitted_at: float = field(default_factory=time.time)
    decided_at: float | None = None


class AppReviewWorkflow:
    """Manage app review and approval workflows."""

    def __init__(self) -> None:
        self._submissions: dict[tuple[str, str], ReviewSubmission] = {}

    def submit_for_review(
        self,
        installation_id: str,
        submission_id: str,
        app_version: str,
        now: float | None = None,
    ) -> ReviewSubmission:
        if not installation_id:
            raise ValueError("installation_id is required")
        if not submission_id:
            raise ValueError("submission_id is required")
        if not app_version:
            raise ValueError("app_version is required")

        key = (installation_id, submission_id)
        if key in self._submissions:
            raise ValueError(f"Submission {submission_id} already exists")

        sub = ReviewSubmission(
            submission_id=submission_id, installation_id=installation_id,
            app_version=app_version, submitted_at=now or time.time(),
        )
        self._submissions[key] = sub
        return sub

    def assign_reviewer(
        self, installation_id: str, submission_id: str, reviewer: str
    ) -> ReviewSubmission:
        sub = self._get(installation_id, submission_id)
        if sub.status != ReviewStatus.PENDING:
            raise ValueError(f"Cannot assign in {sub.status} state")
        if not reviewer:
            raise ValueError("reviewer is required")
        sub.reviewer = reviewer
        sub.status = ReviewStatus.IN_REVIEW
        return sub

    def approve(
        self, installation_id: str, submission_id: str, feedback: str = "",
        now: float | None = None,
    ) -> ReviewSubmission:
        sub = self._get(installation_id, submission_id)
        if sub.status != ReviewStatus.IN_REVIEW:
            raise ValueError("Can only approve from in_review state")
        sub.status = ReviewStatus.APPROVED
        sub.feedback = feedback
        sub.decided_at = now or time.time()
        return sub

    def reject(
        self, installation_id: str, submission_id: str, feedback: str,
        now: float | None = None,
    ) -> ReviewSubmission:
        sub = self._get(installation_id, submission_id)
        if sub.status != ReviewStatus.IN_REVIEW:
            raise ValueError("Can only reject from in_review state")
        if not feedback:
            raise ValueError("Rejection requires feedback")
        sub.status = ReviewStatus.REJECTED
        sub.feedback = feedback
        sub.decided_at = now or time.time()
        return sub

    def request_changes(
        self, installation_id: str, submission_id: str, feedback: str,
    ) -> ReviewSubmission:
        sub = self._get(installation_id, submission_id)
        if sub.status != ReviewStatus.IN_REVIEW:
            raise ValueError("Can only request changes from in_review state")
        if not feedback:
            raise ValueError("Change request requires feedback")
        sub.status = ReviewStatus.CHANGES_REQUESTED
        sub.feedback = feedback
        return sub

    def get_submission(self, installation_id: str, submission_id: str) -> ReviewSubmission:
        return self._get(installation_id, submission_id)

    def list_submissions(
        self, installation_id: str, status: ReviewStatus | None = None
    ) -> list[ReviewSubmission]:
        subs = [s for (inst, _), s in self._submissions.items() if inst == installation_id]
        if status:
            subs = [s for s in subs if s.status == status]
        return subs

    def _get(self, installation_id: str, submission_id: str) -> ReviewSubmission:
        key = (installation_id, submission_id)
        s = self._submissions.get(key)
        if s is None:
            raise KeyError(f"Submission {submission_id} not found")
        return s
