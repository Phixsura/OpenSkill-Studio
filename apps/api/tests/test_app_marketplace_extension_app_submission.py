from app.services.app_marketplace_extension_app_submission import (
    AppSubmissionService, SubmissionStatus,
)
import pytest


def _complete_checklist(svc, sub_id):
    svc.update_checklist(sub_id, has_manifest=True, has_description=True,
                         has_icon=True, has_screenshots=True, has_privacy_policy=True,
                         passes_security_scan=True, passes_content_review=True)


def test_create_draft():
    svc = AppSubmissionService()
    sub = svc.create_draft("ext-1", "dev-1", "1.0.0")
    assert sub.status == SubmissionStatus.DRAFT
    assert sub.checklist.completion_percent == 0


def test_incomplete_submit_rejected():
    svc = AppSubmissionService()
    sub = svc.create_draft("ext-1", "dev-1", "1.0.0")
    result = svc.submit_for_review(sub.submission_id)
    assert result["ok"] is False
    assert "incomplete" in result["error"].lower()


def test_full_workflow():
    svc = AppSubmissionService()
    sub = svc.create_draft("ext-1", "dev-1", "1.0.0")
    _complete_checklist(svc, sub.submission_id)
    result = svc.submit_for_review(sub.submission_id)
    assert result["ok"] is True
    svc.assign_reviewer(sub.submission_id, "reviewer-1")
    assert sub.status == SubmissionStatus.IN_REVIEW
    svc.approve(sub.submission_id, "reviewer-1", "Looks great!")
    assert sub.status == SubmissionStatus.APPROVED


def test_self_review_blocked():
    svc = AppSubmissionService()
    sub = svc.create_draft("ext-1", "dev-1", "1.0.0")
    _complete_checklist(svc, sub.submission_id)
    svc.submit_for_review(sub.submission_id)
    with pytest.raises(PermissionError, match="self-review"):
        svc.assign_reviewer(sub.submission_id, "dev-1")


def test_request_changes():
    svc = AppSubmissionService()
    sub = svc.create_draft("ext-1", "dev-1", "1.0.0")
    _complete_checklist(svc, sub.submission_id)
    svc.submit_for_review(sub.submission_id)
    svc.assign_reviewer(sub.submission_id, "rev-1")
    svc.request_changes(sub.submission_id, "rev-1", "Fix icon resolution")
    assert sub.status == SubmissionStatus.CHANGES_REQUESTED
    assert sub.revision == 2


def test_wrong_reviewer():
    svc = AppSubmissionService()
    sub = svc.create_draft("ext-1", "dev-1", "1.0.0")
    _complete_checklist(svc, sub.submission_id)
    svc.submit_for_review(sub.submission_id)
    svc.assign_reviewer(sub.submission_id, "rev-1")
    with pytest.raises(PermissionError, match="assigned reviewer"):
        svc.approve(sub.submission_id, "rev-2")


def test_checklist_percent():
    svc = AppSubmissionService()
    sub = svc.create_draft("ext-1", "dev-1", "1.0.0")
    svc.update_checklist(sub.submission_id, has_manifest=True, has_description=True)
    assert sub.checklist.completion_percent == 28
