"""Verify every canonical event type individually."""

import pytest
from app.services.event_dispatch import CANONICAL_EVENTS

ALL_EVENTS = sorted(CANONICAL_EVENTS)

@pytest.mark.parametrize("event", ALL_EVENTS)
def test_event_has_dot(event):
    assert "." in event

@pytest.mark.parametrize("event", ALL_EVENTS)
def test_event_lowercase(event):
    assert event == event.lower()

@pytest.mark.parametrize("event", ALL_EVENTS)
def test_event_two_parts(event):
    parts = event.split(".")
    assert len(parts) == 2
    assert len(parts[0]) >= 2
    assert len(parts[1]) >= 2
