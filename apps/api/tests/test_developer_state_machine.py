"""Developer app state machine transitions."""

import pytest

# Inline the allowed transitions (mirrors developer.py)
ALLOWED = {
    "draft": {"testing", "deleted"},
    "testing": {"draft", "submitted", "deleted"},
    "submitted": {"approved", "rejected"},
    "rejected": {"draft"},
    "approved": {"published"},
    "published": {"deprecated", "revoked"},
    "deprecated": {"revoked"},
}

ALL_STATES = list(ALLOWED.keys())

VALID_TRANSITIONS = []
for src, dests in ALLOWED.items():
    for dst in dests:
        VALID_TRANSITIONS.append((src, dst))

INVALID_TRANSITIONS = [
    ("draft", "published"),
    ("draft", "approved"),
    ("testing", "published"),
    ("submitted", "published"),
    ("approved", "draft"),
    ("published", "draft"),
    ("deprecated", "published"),
    ("revoked", "draft"),
]

@pytest.mark.parametrize("src,dst", VALID_TRANSITIONS, ids=lambda x: str(x))
def test_valid_transition(src, dst):
    assert dst in ALLOWED[src]

@pytest.mark.parametrize("src,dst", INVALID_TRANSITIONS)
def test_invalid_transition(src, dst):
    assert dst not in ALLOWED.get(src, set())

@pytest.mark.parametrize("state", ALL_STATES)
def test_no_self_transition(state):
    assert state not in ALLOWED.get(state, set())

def test_draft_is_initial():
    assert "draft" in ALLOWED

def test_revoked_is_terminal():
    assert ALLOWED.get("revoked", set()) == set()

def test_all_states_reachable():
    reachable = set()
    queue = ["draft"]
    while queue:
        s = queue.pop()
        if s in reachable:
            continue
        reachable.add(s)
        queue.extend(ALLOWED.get(s, set()))
    assert {"draft", "testing", "submitted", "approved", "published", "deprecated", "revoked"}.issubset(reachable)
