"""Event dispatch service tests."""

import pytest
from app.services.event_dispatch import (
    _is_safe_url, CANONICAL_EVENTS, PlatformEvent, EventDispatcher,
)

# --- SSRF protection ---

SAFE_URLS = [
    "https://hooks.example.com/webhook",
    "https://api.myapp.io/events",
]

UNSAFE_URLS = [
    "http://127.0.0.1/hook",
    "http://localhost/hook",
    "http://[::1]/hook",
    "http://169.254.169.254/metadata",
    "http://10.0.0.1/internal",
    "http://192.168.1.1/private",
    "http://172.16.0.1/private",
]

@pytest.mark.parametrize("url", UNSAFE_URLS)
def test_unsafe_urls_blocked(url):
    assert _is_safe_url(url) is False

# --- Canonical events ---

EXPECTED_EVENTS = [
    "submission.completed", "submission.graded",
    "cohort.member_added", "cohort.member_removed",
    "project.published",
    "app.installed", "app.uninstalled",
]

@pytest.mark.parametrize("event", EXPECTED_EVENTS)
def test_canonical_event_exists(event):
    assert event in CANONICAL_EVENTS

def test_canonical_events_count():
    assert len(CANONICAL_EVENTS) >= 20

# --- PlatformEvent ---

def test_platform_event_creation():
    e = PlatformEvent(event_type="test.event", data={"key": "val"}, org_id="org-1")
    assert e.event_type == "test.event"
    assert e.org_id == "org-1"

def test_platform_event_to_dict():
    e = PlatformEvent(event_type="test.event", data={"a": 1}, org_id="org-1")
    d = e.to_dict()
    assert d["event_type"] == "test.event"
    assert "event_id" in d
    assert "timestamp" in d

# --- EventDispatcher ---

def test_dispatcher_instantiate():
    d = EventDispatcher()
    assert d is not None

def test_dispatcher_has_emit():
    import inspect
    assert inspect.iscoroutinefunction(EventDispatcher.emit)

def test_dispatcher_filter_matching():
    d = EventDispatcher()
    assert d._matches_filter({"status": "active"}, {"field": "status", "operator": "eq", "value": "active"}) is True
    assert d._matches_filter({"status": "active"}, {"field": "status", "operator": "eq", "value": "inactive"}) is False

def test_dispatcher_flatten():
    d = EventDispatcher()
    result = d._flatten_dict({"a": {"b": "c"}})
    assert "a.b" in result
