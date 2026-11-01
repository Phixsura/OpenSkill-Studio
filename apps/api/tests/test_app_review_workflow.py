"""Tests for App Review Workflow — submit, assign, approve, reject."""

import pytest

from app.services.app_review_workflow import AppReviewWorkflow, ReviewStatus


class TestSubmit:
    def test_submit(self):
        w = AppReviewWorkflow()
        s = w.submit_for_review("inst-1", "s1", "2.0.0")
        assert s.status == ReviewStatus.PENDING

    def test_duplicate(self):
        w = AppReviewWorkflow()
        w.submit_for_review("inst-1", "s1", "2.0.0")
        with pytest.raises(ValueError):
            w.submit_for_review("inst-1", "s1", "2.0.1")


class TestAssign:
    def test_assign(self):
        w = AppReviewWorkflow()
        w.submit_for_review("inst-1", "s1", "2.0.0")
        s = w.assign_reviewer("inst-1", "s1", "reviewer-1")
        assert s.status == ReviewStatus.IN_REVIEW
        assert s.reviewer == "reviewer-1"

    def test_cannot_assign_approved(self):
        w = AppReviewWorkflow()
        w.submit_for_review("inst-1", "s1", "2.0.0")
        w.assign_reviewer("inst-1", "s1", "r1")
        w.approve("inst-1", "s1")
        with pytest.raises(ValueError):
            w.assign_reviewer("inst-1", "s1", "r2")


class TestApprove:
    def test_approve(self):
        w = AppReviewWorkflow()
        w.submit_for_review("inst-1", "s1", "2.0.0")
        w.assign_reviewer("inst-1", "s1", "r1")
        s = w.approve("inst-1", "s1", feedback="Looks good!")
        assert s.status == ReviewStatus.APPROVED

    def test_cannot_approve_pending(self):
        w = AppReviewWorkflow()
        w.submit_for_review("inst-1", "s1", "2.0.0")
        with pytest.raises(ValueError):
            w.approve("inst-1", "s1")


class TestReject:
    def test_reject(self):
        w = AppReviewWorkflow()
        w.submit_for_review("inst-1", "s1", "2.0.0")
        w.assign_reviewer("inst-1", "s1", "r1")
        s = w.reject("inst-1", "s1", feedback="Security issue found")
        assert s.status == ReviewStatus.REJECTED

    def test_reject_requires_feedback(self):
        w = AppReviewWorkflow()
        w.submit_for_review("inst-1", "s1", "2.0.0")
        w.assign_reviewer("inst-1", "s1", "r1")
        with pytest.raises(ValueError, match="feedback"):
            w.reject("inst-1", "s1", feedback="")


class TestChangesRequested:
    def test_request_changes(self):
        w = AppReviewWorkflow()
        w.submit_for_review("inst-1", "s1", "2.0.0")
        w.assign_reviewer("inst-1", "s1", "r1")
        s = w.request_changes("inst-1", "s1", "Fix the API docs")
        assert s.status == ReviewStatus.CHANGES_REQUESTED


class TestList:
    def test_filter_by_status(self):
        w = AppReviewWorkflow()
        w.submit_for_review("inst-1", "s1", "1.0.0")
        w.submit_for_review("inst-1", "s2", "2.0.0")
        w.assign_reviewer("inst-1", "s1", "r1")
        pending = w.list_submissions("inst-1", status=ReviewStatus.PENDING)
        assert len(pending) == 1


class TestIsolation:
    def test_cross_installation(self):
        w = AppReviewWorkflow()
        w.submit_for_review("inst-1", "s1", "1.0.0")
        with pytest.raises(KeyError):
            w.get_submission("inst-2", "s1")
