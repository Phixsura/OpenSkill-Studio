"""Canonical events — complete set validation."""

import pytest
from app.services.event_dispatch import CANONICAL_EVENTS

# Events should follow category.action naming
@pytest.mark.parametrize("event", sorted(CANONICAL_EVENTS))
def test_event_naming_convention(event):
    parts = event.split(".")
    assert len(parts) == 2, f"{event} should be 'category.action'"
    assert len(parts[0]) > 0, f"{event} has empty category"
    assert len(parts[1]) > 0, f"{event} has empty action"

# Expected event categories
EXPECTED_CATEGORIES = {"submission", "cohort", "project", "pack", "workflow", "app", "evaluation", "talent", "marketplace"}

def test_all_expected_categories_present():
    actual_categories = {e.split(".")[0] for e in CANONICAL_EVENTS}
    missing = EXPECTED_CATEGORIES - actual_categories
    assert missing == set(), f"Missing event categories: {missing}"

def test_canonical_events_is_frozen():
    assert isinstance(CANONICAL_EVENTS, frozenset)

def test_no_duplicate_events():
    as_list = list(CANONICAL_EVENTS)
    assert len(as_list) == len(set(as_list))

def test_all_lowercase():
    for event in CANONICAL_EVENTS:
        assert event == event.lower(), f"{event} should be lowercase"
