"""Tests for App Event Replay — store, replay, filter."""

import pytest

from app.services.app_event_replay import AppEventReplay


class TestStore:
    def test_store(self):
        r = AppEventReplay()
        e = r.store("inst-1", "e1", "webhook.sent", "api", {"url": "https://example.com"})
        assert e.event_type == "webhook.sent"
        assert e.replayed is False

    def test_retention(self):
        r = AppEventReplay(max_events=3)
        for i in range(5):
            r.store("inst-1", f"e{i}", "test", "api", {})
        assert r.count("inst-1") == 3


class TestReplay:
    def test_replay_all(self):
        r = AppEventReplay()
        r.store("inst-1", "e1", "webhook.sent", "api", {})
        r.store("inst-1", "e2", "user.created", "auth", {})
        events = r.replay("inst-1")
        assert len(events) == 2
        assert all(e.replayed for e in events)

    def test_filter_by_type(self):
        r = AppEventReplay()
        r.store("inst-1", "e1", "webhook.sent", "api", {})
        r.store("inst-1", "e2", "user.created", "auth", {})
        events = r.replay("inst-1", event_type="webhook.sent")
        assert len(events) == 1

    def test_filter_by_source(self):
        r = AppEventReplay()
        r.store("inst-1", "e1", "webhook.sent", "api", {})
        r.store("inst-1", "e2", "user.created", "auth", {})
        events = r.replay("inst-1", source="auth")
        assert len(events) == 1


class TestEventTypes:
    def test_types(self):
        r = AppEventReplay()
        r.store("inst-1", "e1", "webhook.sent", "api", {})
        r.store("inst-1", "e2", "user.created", "auth", {})
        assert r.event_types("inst-1") == ["user.created", "webhook.sent"]


class TestIsolation:
    def test_cross(self):
        r = AppEventReplay()
        r.store("inst-1", "e1", "test", "api", {})
        assert r.count("inst-2") == 0
