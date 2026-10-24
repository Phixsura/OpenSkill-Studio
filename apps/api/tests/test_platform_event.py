"""PlatformEvent construction and serialization."""

import pytest
from app.services.event_dispatch import PlatformEvent, CANONICAL_EVENTS


def test_event_has_id():
    e = PlatformEvent(event_type="test.event", data={}, org_id="org-1")
    assert e.event_id and len(e.event_id) > 0

def test_event_unique_ids():
    e1 = PlatformEvent(event_type="test.event", data={}, org_id="org-1")
    e2 = PlatformEvent(event_type="test.event", data={}, org_id="org-1")
    assert e1.event_id != e2.event_id

def test_event_has_timestamp():
    e = PlatformEvent(event_type="test.event", data={}, org_id="org-1")
    assert e.timestamp is not None

def test_to_dict_complete():
    e = PlatformEvent(event_type="app.installed", data={"app_id": "a1"}, org_id="org-1")
    d = e.to_dict()
    assert d["event_type"] == "app.installed"
    assert d["data"]["app_id"] == "a1"
    assert "event_id" in d
    assert "timestamp" in d

@pytest.mark.parametrize("event_type", sorted(list(CANONICAL_EVENTS))[:15])
def test_canonical_events_roundtrip(event_type):
    e = PlatformEvent(event_type=event_type, data={"test": True}, org_id="org-x")
    d = e.to_dict()
    assert d["event_type"] == event_type


def test_canonical_events_frozen():
    with pytest.raises((TypeError, AttributeError)):
        CANONICAL_EVENTS.add("fake.event")
