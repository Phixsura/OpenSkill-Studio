"""Tests for App User Activity Feed — record, query, filters, summary."""

import pytest

from app.services.app_user_activity_feed import AppUserActivityFeed


class TestRecord:
    def test_record(self):
        f = AppUserActivityFeed()
        e = f.record("inst-1", "e1", "user-1", "created", "project", "p1", now=1000.0)
        assert e.action == "created"
        assert f.event_count("inst-1") == 1

    def test_missing_action(self):
        f = AppUserActivityFeed()
        with pytest.raises(ValueError, match="action"):
            f.record("inst-1", "e1", "user-1", "", "project", "p1")


class TestFeed:
    def test_newest_first(self):
        f = AppUserActivityFeed()
        f.record("inst-1", "e1", "u1", "created", "project", "p1", now=1000.0)
        f.record("inst-1", "e2", "u1", "updated", "project", "p1", now=2000.0)
        feed = f.get_feed("inst-1")
        assert feed[0].event_id == "e2"

    def test_filter_user(self):
        f = AppUserActivityFeed()
        f.record("inst-1", "e1", "u1", "created", "project", "p1")
        f.record("inst-1", "e2", "u2", "created", "project", "p2")
        feed = f.get_feed("inst-1", user_id="u1")
        assert len(feed) == 1

    def test_filter_action(self):
        f = AppUserActivityFeed()
        f.record("inst-1", "e1", "u1", "created", "project", "p1")
        f.record("inst-1", "e2", "u1", "deleted", "project", "p2")
        feed = f.get_feed("inst-1", action="created")
        assert len(feed) == 1

    def test_filter_resource(self):
        f = AppUserActivityFeed()
        f.record("inst-1", "e1", "u1", "created", "project", "p1")
        f.record("inst-1", "e2", "u1", "created", "file", "f1")
        feed = f.get_feed("inst-1", resource_type="file")
        assert len(feed) == 1

    def test_limit(self):
        f = AppUserActivityFeed()
        for i in range(10):
            f.record("inst-1", f"e{i}", "u1", "viewed", "page", f"p{i}")
        feed = f.get_feed("inst-1", limit=3)
        assert len(feed) == 3


class TestSummary:
    def test_user_summary(self):
        f = AppUserActivityFeed()
        f.record("inst-1", "e1", "u1", "created", "p", "1")
        f.record("inst-1", "e2", "u1", "created", "p", "2")
        f.record("inst-1", "e3", "u1", "deleted", "p", "1")
        summary = f.get_user_summary("inst-1", "u1")
        assert summary["created"] == 2
        assert summary["deleted"] == 1


class TestIsolation:
    def test_cross_installation(self):
        f = AppUserActivityFeed()
        f.record("inst-1", "e1", "u1", "created", "p", "1")
        assert f.event_count("inst-2") == 0
