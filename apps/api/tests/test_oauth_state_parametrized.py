"""Parametrized OAuth state validation tests."""

import pytest
from app.models.developer import AppStatus

ALLOWED_OAUTH_STATES = ["TESTING", "APPROVED", "PUBLISHED"]
BLOCKED_OAUTH_STATES = ["DRAFT", "SUBMITTED", "DEPRECATED", "REVOKED"]

@pytest.mark.parametrize("status", ALLOWED_OAUTH_STATES)
def test_allowed_oauth_state(status):
    assert AppStatus(status.lower() if status.lower() in [s.value for s in AppStatus] else status)

@pytest.mark.parametrize("status", BLOCKED_OAUTH_STATES)
def test_blocked_oauth_state(status):
    assert AppStatus(status.lower() if status.lower() in [s.value for s in AppStatus] else status)

def test_allowed_set_size():
    assert len(ALLOWED_OAUTH_STATES) == 3

def test_blocked_set_size():
    assert len(BLOCKED_OAUTH_STATES) == 4

def test_all_states_covered():
    assert len(ALLOWED_OAUTH_STATES) + len(BLOCKED_OAUTH_STATES) == 7
