"""AppReviewSubmission model tests."""

import pytest
from app.models.developer import AppReviewSubmission

REQUIRED = ["id", "app_id", "app_version_id", "submitted_by", "review_status"]

@pytest.mark.parametrize("col", REQUIRED)
def test_required(col):
    assert col in {c.name for c in AppReviewSubmission.__table__.columns}

OPTIONAL = ["reviewer_id", "review_notes", "automated_checks", "reviewed_at"]

@pytest.mark.parametrize("col", OPTIONAL)
def test_optional(col):
    assert col in {c.name for c in AppReviewSubmission.__table__.columns}

def test_app_id_fk():
    assert len(AppReviewSubmission.__table__.columns["app_id"].foreign_keys) > 0

def test_app_version_id_fk():
    assert len(AppReviewSubmission.__table__.columns["app_version_id"].foreign_keys) > 0
