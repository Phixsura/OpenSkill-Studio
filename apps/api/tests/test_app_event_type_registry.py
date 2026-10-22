"""Event type registry tests."""
import pytest
from app.services.app_event_type_registry import get_event_info, list_event_types, get_events_by_category, EVENT_REGISTRY

def test_registry_populated():
    assert len(EVENT_REGISTRY) >= 20

def test_get_known_event():
    info = get_event_info("submission.completed")
    assert info is not None
    assert info.category == "submission"
    assert len(info.payload_fields) > 0

def test_get_unknown():
    assert get_event_info("nonexistent.event") is None

def test_list_sorted():
    events = list_event_types()
    names = [e.name for e in events]
    assert names == sorted(names)

def test_by_category():
    sub_events = get_events_by_category("submission")
    assert len(sub_events) >= 2
    assert all(e.category == "submission" for e in sub_events)

def test_app_events():
    app_events = get_events_by_category("app")
    assert len(app_events) >= 2
