"""Tests for App Log Drain — add, filter, delivery stats."""

import pytest

from app.services.app_log_drain import AppLogDrain


class TestAddDrain:
    def test_add(self):
        d = AppLogDrain()
        drain = d.add_drain("inst-1", "d1", "https://logs.example.com", "http", "warn")
        assert drain.min_level == "warn"
        assert drain.enabled is True

    def test_invalid_type(self):
        d = AppLogDrain()
        with pytest.raises(ValueError, match="drain_type"):
            d.add_drain("inst-1", "d1", "udp://logs", "udp")


class TestFilter:
    def test_level_filter(self):
        d = AppLogDrain()
        d.add_drain("inst-1", "d1", "https://logs", "http", "warn")
        assert d.should_forward("inst-1", "d1", "error") is True
        assert d.should_forward("inst-1", "d1", "info") is False

    def test_source_filter(self):
        d = AppLogDrain()
        d.add_drain("inst-1", "d1", "https://logs", source_filter="api")
        assert d.should_forward("inst-1", "d1", "info", "api-server") is True
        assert d.should_forward("inst-1", "d1", "info", "worker") is False

    def test_disabled(self):
        d = AppLogDrain()
        d.add_drain("inst-1", "d1", "https://logs")
        d.toggle("inst-1", "d1", False)
        assert d.should_forward("inst-1", "d1", "error") is False


class TestStats:
    def test_delivery(self):
        d = AppLogDrain()
        d.add_drain("inst-1", "d1", "https://logs")
        d.record_delivery("inst-1", "d1", True)
        d.record_delivery("inst-1", "d1", True)
        d.record_delivery("inst-1", "d1", False)
        stats = d.get_stats("inst-1", "d1")
        assert stats.sent == 2
        assert stats.failed == 1
        assert stats.success_rate == 66.7

    def test_drop(self):
        d = AppLogDrain()
        d.add_drain("inst-1", "d1", "https://logs")
        d.record_drop("inst-1", "d1")
        assert d.get_stats("inst-1", "d1").dropped == 1


class TestIsolation:
    def test_cross(self):
        d = AppLogDrain()
        d.add_drain("inst-1", "d1", "https://logs")
        assert d.list_drains("inst-2") == []
