"""Parametrized event subscription manifest validation tests."""

import pytest
from app.services.manifest_validator import validate_manifest

VALID_EVENT_COMBOS = [
    [],
    ["submission.completed"],
    ["submission.completed", "cohort.member_added"],
    ["pack.published", "workflow.run_completed", "app.installed"],
]

@pytest.mark.parametrize("events", VALID_EVENT_COMBOS)
def test_valid_event_subscriptions(events):
    r = validate_manifest({
        "schema_version": "1.0", "app": {"name": "T"},
        "permissions": ["subscribe:events"] if events else [],
        "event_subscriptions": events,
    })
    event_errors = [e for e in r.errors if "event" in e.lower()]
    assert event_errors == []

def test_events_without_permission_warns():
    r = validate_manifest({
        "schema_version": "1.0", "app": {"name": "T"},
        "event_subscriptions": ["submission.completed"],
    })
    assert any("subscribe:events" in w for w in r.warnings)

def test_events_with_permission_no_warn():
    r = validate_manifest({
        "schema_version": "1.0", "app": {"name": "T"},
        "permissions": ["subscribe:events"],
        "event_subscriptions": ["submission.completed"],
    })
    event_warns = [w for w in r.warnings if "subscribe" in w]
    assert event_warns == []

def test_non_string_event():
    r = validate_manifest({
        "schema_version": "1.0", "app": {"name": "T"},
        "permissions": ["subscribe:events"],
        "event_subscriptions": [123],
    })
    assert any("string" in e for e in r.errors)
