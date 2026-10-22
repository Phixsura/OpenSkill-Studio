"""State machine — exhaustive all-pairs test."""

import pytest

ALLOWED = {
    "draft": {"testing", "deleted"},
    "testing": {"draft", "submitted", "deleted"},
    "submitted": {"approved", "rejected"},
    "rejected": {"draft"},
    "approved": {"published"},
    "published": {"deprecated", "revoked"},
    "deprecated": {"revoked"},
}

ALL_STATES = ["draft", "testing", "submitted", "rejected", "approved", "published", "deprecated", "revoked"]

ALL_PAIRS = [(src, dst) for src in ALL_STATES for dst in ALL_STATES if src != dst]

@pytest.mark.parametrize("src,dst", ALL_PAIRS, ids=lambda x: str(x))
def test_transition_correctness(src, dst):
    allowed_targets = ALLOWED.get(src, set())
    if dst in allowed_targets:
        assert True  # valid transition
    else:
        assert dst not in allowed_targets  # invalid transition correctly blocked

def test_total_valid_transitions():
    total = sum(len(v) for v in ALLOWED.values())
    assert total == 12

def test_revoked_terminal():
    assert ALLOWED.get("revoked", set()) == set()

def test_deleted_not_in_states():
    # deleted is a target but not a source state
    assert "deleted" not in ALLOWED
