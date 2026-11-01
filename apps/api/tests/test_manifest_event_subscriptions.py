"""Manifest event subscription validation."""

import pytest
from app.services.manifest_validator import validate_manifest
from app.services.event_dispatch import CANONICAL_EVENTS

BASE = {
    "schema_version": "1.0",
    "app": {"name": "Evt", "slug": "evt-app", "version": "1.0.0", "category": "automation"},
    "permissions": ["read:cohorts", "subscribe:events"],
}

SAMPLE_EVENTS = sorted(list(CANONICAL_EVENTS))[:10]

@pytest.mark.parametrize("event", SAMPLE_EVENTS)
def test_canonical_event_accepted(event):
    m = {**BASE, "event_subscriptions": [event]}
    r = validate_manifest(m)
    event_errors = [e for e in r.errors if "event" in e.lower() and "subscription" in e.lower()]
    assert event_errors == [], f"{event}: {event_errors}"

def test_multiple_subscriptions():
    m = {**BASE, "event_subscriptions": list(CANONICAL_EVENTS)[:5]}
    r = validate_manifest(m)
    assert r.valid, f"Errors: {r.errors}"

def test_empty_subscriptions():
    m = {**BASE, "event_subscriptions": []}
    r = validate_manifest(m)
    assert r.valid, f"Errors: {r.errors}"
