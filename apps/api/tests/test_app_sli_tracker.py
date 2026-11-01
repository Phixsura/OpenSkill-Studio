"""Tests for App SLI Tracker — record, report, targets."""

import pytest

from app.services.app_sli_tracker import AppSLITracker


class TestRecord:
    def test_record(self):
        t = AppSLITracker()
        m = t.record("inst-1", "availability", 99.95)
        assert m.value == 99.95


class TestReport:
    def test_report(self):
        t = AppSLITracker()
        t.record("inst-1", "availability", 99.9)
        t.record("inst-1", "availability", 99.8)
        t.record("inst-1", "availability", 100.0)
        r = t.get_report("inst-1", "availability")
        assert r.current == 100.0
        assert r.min_val == 99.8
        assert r.max_val == 100.0
        assert r.measurement_count == 3

    def test_empty_report(self):
        t = AppSLITracker()
        r = t.get_report("inst-1", "nope")
        assert r.measurement_count == 0
        assert r.meets_target is True


class TestTargets:
    def test_meets_target(self):
        t = AppSLITracker()
        t.set_target("inst-1", "availability", 99.9)
        t.record("inst-1", "availability", 99.95)
        r = t.get_report("inst-1", "availability")
        assert r.meets_target is True

    def test_below_target(self):
        t = AppSLITracker()
        t.set_target("inst-1", "availability", 99.9)
        t.record("inst-1", "availability", 99.5)
        r = t.get_report("inst-1", "availability")
        assert r.meets_target is False


class TestListMetrics:
    def test_list(self):
        t = AppSLITracker()
        t.record("inst-1", "availability", 99.9)
        t.record("inst-1", "latency_p99", 150)
        assert t.list_metrics("inst-1") == ["availability", "latency_p99"]


class TestIsolation:
    def test_cross_installation(self):
        t = AppSLITracker()
        t.record("inst-1", "availability", 99.9)
        assert t.list_metrics("inst-2") == []
