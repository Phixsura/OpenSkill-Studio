"""Event subscription schema tests."""

import pytest
from pydantic import ValidationError
from app.schemas.developer import CreateEventSubscriptionRequest

EVENTS = ["submission.completed", "submission.graded", "cohort.member_added", "app.installed"]

@pytest.mark.parametrize("event", EVENTS)
def test_valid_event_types(event):
    r = CreateEventSubscriptionRequest(event_type=event)
    assert r.event_type == event

def test_missing_event_type():
    with pytest.raises(ValidationError):
        CreateEventSubscriptionRequest()

def test_serialization():
    r = CreateEventSubscriptionRequest(event_type="app.installed")
    d = r.model_dump()
    assert d["event_type"] == "app.installed"
