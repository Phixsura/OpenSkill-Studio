"""PlatformEvent + EventDispatcher full integration."""

import pytest
from app.services.event_dispatch import PlatformEvent, EventDispatcher, CANONICAL_EVENTS


def test_create_and_serialize_all_canonical():
    """Create a PlatformEvent for every canonical event and serialize."""
    for event_type in CANONICAL_EVENTS:
        e = PlatformEvent(event_type=event_type, data={"test": True}, org_id="org-1")
        d = e.to_dict()
        assert d["event_type"] == event_type
        assert "event_id" in d
        assert "timestamp" in d


def test_dispatcher_flatten_nested_event():
    d = EventDispatcher()
    event_data = {
        "submission": {
            "id": "sub-1",
            "project": {"id": "proj-1", "name": "Test"},
            "user_id": "u-1",
        },
        "scores": [90, 85, 92],
    }
    flat = d._flatten_dict(event_data)
    assert "submission.id" in flat
    assert "submission.project.id" in flat
    assert "submission.user_id" in flat


def test_filter_on_nested_event_data():
    d = EventDispatcher()
    data = {"submission": {"status": "graded", "score": 95}}
    
    # Match
    assert d._matches_filter(data, {"field": "submission.status", "operator": "eq", "value": "graded"})
    # No match
    assert not d._matches_filter(data, {"field": "submission.status", "operator": "eq", "value": "pending"})
    # GTE
    assert d._matches_filter(data, {"field": "submission.score", "operator": "gte", "value": 90})
    # LTE
    assert d._matches_filter(data, {"field": "submission.score", "operator": "lte", "value": 100})
