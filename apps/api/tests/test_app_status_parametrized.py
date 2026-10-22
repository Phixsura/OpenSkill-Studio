"""Parametrized tests for app status lifecycle."""

import pytest
from app.models.developer import AppStatus

ALL_STATUSES = sorted([s.value for s in AppStatus])

@pytest.mark.parametrize("status", ALL_STATUSES)
def test_status_is_string(status):
    assert isinstance(status, str)

@pytest.mark.parametrize("status", ALL_STATUSES)
def test_status_lowercase(status):
    assert status == status.lower()

@pytest.mark.parametrize("status", ALL_STATUSES)
def test_status_in_enum(status):
    assert AppStatus(status) is not None

def test_lifecycle_order():
    lifecycle = ["draft", "testing", "submitted", "approved", "published", "deprecated", "revoked"]
    for s in lifecycle:
        assert s in ALL_STATUSES

def test_status_count():
    assert len(AppStatus) == 7
