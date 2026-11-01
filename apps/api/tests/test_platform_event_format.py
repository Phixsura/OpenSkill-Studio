"""PlatformEvent format tests."""

import pytest
from app.services.event_dispatch import PlatformEvent

EVENTS = [
    ("submission.completed", {"id": "s1"}, "org-1", "user-1"),
    ("cohort.member_added", {"cohort_id": "c1"}, "org-2", None),
    ("app.installed", {"app_id": "a1"}, None, "user-2"),
    ("pack.published", {}, "org-3", "user-3"),
]

@pytest.mark.parametrize("event_type,data,org_id,user_id", EVENTS)
def test_event_creation(event_type, data, org_id, user_id):
    e = PlatformEvent(event_type, data, org_id=org_id, user_id=user_id)
    assert e.event_type == event_type
    assert e.data == data
    assert e.org_id == org_id
    assert e.user_id == user_id
    assert e.event_id
    assert e.timestamp

@pytest.mark.parametrize("event_type,data,org_id,user_id", EVENTS)
def test_event_to_dict(event_type, data, org_id, user_id):
    e = PlatformEvent(event_type, data, org_id=org_id, user_id=user_id)
    d = e.to_dict()
    assert d["event_type"] == event_type
    assert d["data"] == data
    assert "event_id" in d
    assert "timestamp" in d
