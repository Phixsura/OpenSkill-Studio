"""Tests for App Digest Builder — events, digest compilation, categories."""

import pytest

from app.services.app_digest_builder import AppDigestBuilder, DigestPeriod


class TestAddEvent:
    def test_add(self):
        b = AppDigestBuilder()
        e = b.add_event("inst-1", "user.signup", "New user signed up", now=1000.0)
        assert e.event_type == "user.signup"
        assert b.event_count("inst-1") == 1

    def test_missing_type(self):
        b = AppDigestBuilder()
        with pytest.raises(ValueError, match="event_type"):
            b.add_event("inst-1", "", "title")

    def test_missing_title(self):
        b = AppDigestBuilder()
        with pytest.raises(ValueError, match="title"):
            b.add_event("inst-1", "type", "")


class TestBuildDigest:
    def test_build(self):
        b = AppDigestBuilder()
        b.add_event("inst-1", "user.signup", "User A", category="users", now=1000.0)
        b.add_event("inst-1", "user.signup", "User B", category="users", now=1001.0)
        b.add_event("inst-1", "order.created", "Order 1", category="orders", now=1002.0)
        d = b.build_digest("inst-1", "d1", DigestPeriod.DAILY, 999.0, 1003.0)
        assert d.total_events == 3
        assert d.by_category["users"] == 2
        assert d.by_category["orders"] == 1

    def test_top_event_types(self):
        b = AppDigestBuilder()
        for _ in range(5):
            b.add_event("inst-1", "user.signup", "User", now=1000.0)
        for _ in range(3):
            b.add_event("inst-1", "order.created", "Order", now=1000.0)
        d = b.build_digest("inst-1", "d1", DigestPeriod.DAILY, 999.0, 1001.0)
        assert d.top_event_types[0] == ("user.signup", 5)

    def test_window_filtering(self):
        b = AppDigestBuilder()
        b.add_event("inst-1", "a", "Before", now=500.0)
        b.add_event("inst-1", "b", "Inside", now=1000.0)
        b.add_event("inst-1", "c", "After", now=2000.0)
        d = b.build_digest("inst-1", "d1", DigestPeriod.HOURLY, 999.0, 1001.0)
        assert d.total_events == 1

    def test_invalid_range(self):
        b = AppDigestBuilder()
        with pytest.raises(ValueError, match="end_at"):
            b.build_digest("inst-1", "d1", DigestPeriod.DAILY, 1000.0, 999.0)

    def test_empty_digest(self):
        b = AppDigestBuilder()
        d = b.build_digest("inst-1", "d1", DigestPeriod.DAILY, 1000.0, 2000.0)
        assert d.total_events == 0
        assert d.by_category == {}


class TestGetDigest:
    def test_get(self):
        b = AppDigestBuilder()
        b.build_digest("inst-1", "d1", DigestPeriod.DAILY, 0, 1)
        d = b.get_digest("inst-1", "d1")
        assert d.digest_id == "d1"

    def test_not_found(self):
        b = AppDigestBuilder()
        with pytest.raises(KeyError):
            b.get_digest("inst-1", "nope")


class TestIsolation:
    def test_cross_installation(self):
        b = AppDigestBuilder()
        b.add_event("inst-1", "a", "Event", now=1000.0)
        d = b.build_digest("inst-2", "d1", DigestPeriod.DAILY, 999.0, 1001.0)
        assert d.total_events == 0
