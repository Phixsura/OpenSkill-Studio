"""App Submission — manage extension submission workflow for marketplace listing.

Handles the full submission lifecycle: draft → submitted → in_review →
approved/rejected, with checklist validation, reviewer assignment,
and revision tracking.
"""
from __future__ import annotations
import secrets
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum


class SubmissionStatus(str, Enum):
    DRAFT = "draft"
    SUBMITTED = "submitted"
    IN_REVIEW = "in_review"
    CHANGES_REQUESTED = "changes_requested"
    APPROVED = "approved"
    REJECTED = "rejected"
    PUBLISHED = "published"


@dataclass
class SubmissionChecklist:
    has_manifest: bool = False
    has_description: bool = False
    has_icon: bool = False
    has_screenshots: bool = False
    has_privacy_policy: bool = False
    passes_security_scan: bool = False
    passes_content_review: bool = False

    @property
    def complete(self) -> bool:
        return all([
            self.has_manifest, self.has_description, self.has_icon,
            self.has_screenshots, self.has_privacy_policy,
            self.passes_security_scan, self.passes_content_review,
        ])

    @property
    def completion_percent(self) -> int:
        items = [self.has_manifest, self.has_description, self.has_icon,
                 self.has_screenshots, self.has_privacy_policy,
                 self.passes_security_scan, self.passes_content_review]
        return int(sum(items) / len(items) * 100)


@dataclass
class Submission:
    submission_id: str
    extension_id: str
    developer_id: str
    version: str
    status: SubmissionStatus = SubmissionStatus.DRAFT
    checklist: SubmissionChecklist = field(default_factory=SubmissionChecklist)
    reviewer_id: str = ""
    review_notes: str = ""
    rejection_reason: str = ""
    revision: int = 1
    created_at: str = ""
    submitted_at: str = ""

    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.now(timezone.utc).isoformat()


class AppSubmissionService:
    """Manages the extension submission and review workflow."""

    def __init__(self):
        self._submissions: dict[str, Submission] = {}

    def create_draft(self, extension_id: str, developer_id: str,
                     version: str) -> Submission:
        sub_id = f"sub_{secrets.token_urlsafe(10)}"
        sub = Submission(
            submission_id=sub_id, extension_id=extension_id,
            developer_id=developer_id, version=version,
        )
        self._submissions[sub_id] = sub
        return sub

    def update_checklist(self, submission_id: str, **kwargs: bool) -> SubmissionChecklist | None:
        sub = self._submissions.get(submission_id)
        if not sub or sub.status not in (SubmissionStatus.DRAFT, SubmissionStatus.CHANGES_REQUESTED):
            return None
        for key, val in kwargs.items():
            if hasattr(sub.checklist, key):
                setattr(sub.checklist, key, val)
        return sub.checklist

    def submit_for_review(self, submission_id: str) -> dict:
        sub = self._submissions.get(submission_id)
        if not sub:
            return {"ok": False, "error": "Submission not found"}
        if sub.status not in (SubmissionStatus.DRAFT, SubmissionStatus.CHANGES_REQUESTED):
            return {"ok": False, "error": f"Cannot submit from {sub.status.value}"}
        if not sub.checklist.complete:
            return {"ok": False, "error": "Checklist incomplete",
                    "completion": sub.checklist.completion_percent}
        sub.status = SubmissionStatus.SUBMITTED
        sub.submitted_at = datetime.now(timezone.utc).isoformat()
        return {"ok": True, "submission_id": submission_id}

    def assign_reviewer(self, submission_id: str, reviewer_id: str) -> bool:
        sub = self._submissions.get(submission_id)
        if not sub or sub.status != SubmissionStatus.SUBMITTED:
            return False
        if reviewer_id == sub.developer_id:
            raise PermissionError("Cannot self-review")
        sub.reviewer_id = reviewer_id
        sub.status = SubmissionStatus.IN_REVIEW
        return True

    def approve(self, submission_id: str, reviewer_id: str, notes: str = "") -> bool:
        sub = self._submissions.get(submission_id)
        if not sub or sub.status != SubmissionStatus.IN_REVIEW:
            return False
        if sub.reviewer_id != reviewer_id:
            raise PermissionError("Not the assigned reviewer")
        sub.status = SubmissionStatus.APPROVED
        sub.review_notes = notes
        return True

    def reject(self, submission_id: str, reviewer_id: str, reason: str) -> bool:
        sub = self._submissions.get(submission_id)
        if not sub or sub.status != SubmissionStatus.IN_REVIEW:
            return False
        if sub.reviewer_id != reviewer_id:
            raise PermissionError("Not the assigned reviewer")
        sub.status = SubmissionStatus.REJECTED
        sub.rejection_reason = reason
        return True

    def request_changes(self, submission_id: str, reviewer_id: str, notes: str) -> bool:
        sub = self._submissions.get(submission_id)
        if not sub or sub.status != SubmissionStatus.IN_REVIEW:
            return False
        if sub.reviewer_id != reviewer_id:
            raise PermissionError("Not the assigned reviewer")
        sub.status = SubmissionStatus.CHANGES_REQUESTED
        sub.review_notes = notes
        sub.revision += 1
        return True

    def get_queue(self, status: SubmissionStatus | None = None) -> list[Submission]:
        subs = list(self._submissions.values())
        if status:
            subs = [s for s in subs if s.status == status]
        return subs
