"""Tests for App SLA Tracker — targets, measurements, compliance, breaches."""

import pytest

from app.services.app_sla_tracker import AppSLATracker


class TestDefineTarget:
    def test_define(self):
        t = AppSLATracker()
        target = t.define_target("inst-1", "uptime", "Uptime SLA", "uptime_pct", 99.9, "gte")
        assert target.target_id == "uptime"
        assert target.threshold == 99.9

    def test_invalid_comparison(self):
        t = AppSLATracker()
        with pytest.raises(ValueError, match="comparison"):
            t.define_target("inst-1", "t1", "X", "x", 0, "eq")


class TestRecord:
    def test_met(self):
        t = AppSLATracker()
        t.define_target("inst-1", "uptime", "Uptime", "uptime_pct", 99.9, "gte")
        m = t.record("inst-1", "uptime", 99.95)
        assert m.met is True

    def test_breach(self):
        t = AppSLATracker()
        t.define_target("inst-1", "uptime", "Uptime", "uptime_pct", 99.9, "gte")
        m = t.record("inst-1", "uptime", 99.5)
        assert m.met is False

    def test_lte_comparison(self):
        t = AppSLATracker()
        t.define_target("inst-1", "latency", "Latency", "response_time_ms", 200, "lte")
        m1 = t.record("inst-1", "latency", 150)
        assert m1.met is True
        m2 = t.record("inst-1", "latency", 250)
        assert m2.met is False

    def test_unknown_target(self):
        t = AppSLATracker()
        with pytest.raises(KeyError):
            t.record("inst-1", "nope", 100)


class TestStatus:
    def test_compliance(self):
        t = AppSLATracker()
        t.define_target("inst-1", "uptime", "Uptime", "uptime_pct", 99.9, "gte")
        for v in [99.95, 99.92, 99.5, 99.99]:
            t.record("inst-1", "uptime", v)
        s = t.get_status("inst-1", "uptime")
        assert s.measurements == 4
        assert s.breaches == 1
        assert s.compliance_pct == 75.0

    def test_current_value(self):
        t = AppSLATracker()
        t.define_target("inst-1", "uptime", "Uptime", "uptime_pct", 99.9, "gte")
        t.record("inst-1", "uptime", 99.5)
        t.record("inst-1", "uptime", 99.99)
        s = t.get_status("inst-1", "uptime")
        assert s.current_value == 99.99
        assert s.met is True

    def test_no_measurements(self):
        t = AppSLATracker()
        t.define_target("inst-1", "uptime", "Uptime", "uptime_pct", 99.9, "gte")
        s = t.get_status("inst-1", "uptime")
        assert s.compliance_pct == 100.0
        assert s.measurements == 0

    def test_all_breaches(self):
        t = AppSLATracker()
        t.define_target("inst-1", "uptime", "Uptime", "uptime_pct", 99.9, "gte")
        for _ in range(3):
            t.record("inst-1", "uptime", 90.0)
        s = t.get_status("inst-1", "uptime")
        assert s.compliance_pct == 0.0
        assert s.breaches == 3


class TestListTargets:
    def test_list(self):
        t = AppSLATracker()
        t.define_target("inst-1", "t1", "A", "x", 1)
        t.define_target("inst-1", "t2", "B", "y", 2)
        assert len(t.list_targets("inst-1")) == 2


class TestIsolation:
    def test_cross_installation(self):
        t = AppSLATracker()
        t.define_target("inst-1", "t1", "A", "x", 1)
        with pytest.raises(KeyError):
            t.get_status("inst-2", "t1")
