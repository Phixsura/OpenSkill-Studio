"""Tests for Consumer SLA Tracker service."""
import pytest
from app.services.app_api_developer_platform_sdk_consumer_api_sla_tracker import (
    SlaTracker, SlaTarget,
)


class TestSlaTracker:
    def test_define_and_record_met(self):
        svc = SlaTracker()
        svc.define_sla(SlaTarget("s1", "c1", "latency_p99_ms", 200.0, "lte"))
        result = svc.record("s1", 150.0, "2024-01")
        assert result["met"] is True

    def test_record_breach(self):
        svc = SlaTracker()
        svc.define_sla(SlaTarget("s1", "c1", "latency_p99_ms", 200.0, "lte"))
        result = svc.record("s1", 250.0, "2024-01")
        assert result["met"] is False

    def test_compliance_tracking(self):
        svc = SlaTracker()
        svc.define_sla(SlaTarget("s1", "c1", "uptime_pct", 99.9, "gte"))
        for i in range(10):
            svc.record("s1", 99.95, f"2024-{i+1:02d}")
        svc.record("s1", 99.5, "2024-11")
        compliance = svc.get_compliance("s1")
        assert compliance["met_count"] == 10
        assert compliance["breach_count"] == 1

    def test_compliance_status_compliant(self):
        svc = SlaTracker()
        svc.define_sla(SlaTarget("s1", "c1", "error_rate_pct", 1.0, "lte"))
        for i in range(100):
            svc.record("s1", 0.5, f"p{i}")
        assert svc.get_compliance("s1")["status"] == "compliant"

    def test_compliance_status_breached(self):
        svc = SlaTracker()
        svc.define_sla(SlaTarget("s1", "c1", "error_rate_pct", 1.0, "lte"))
        for i in range(10):
            svc.record("s1", 2.0, f"p{i}")
        assert svc.get_compliance("s1")["status"] == "breached"

    def test_consumer_summary(self):
        svc = SlaTracker()
        svc.define_sla(SlaTarget("s1", "c1", "uptime_pct", 99.9, "gte"))
        svc.define_sla(SlaTarget("s2", "c1", "latency_p99_ms", 300.0, "lte"))
        svc.record("s1", 99.95, "p1")
        svc.record("s2", 250.0, "p1")
        summary = svc.get_consumer_summary("c1")
        assert summary["sla_count"] == 2
        assert summary["overall_status"] == "compliant"

    def test_operator_gte(self):
        svc = SlaTracker()
        svc.define_sla(SlaTarget("s1", "c1", "uptime", 99.0, "gte"))
        assert svc.record("s1", 99.5, "p1")["met"] is True
        assert svc.record("s1", 98.0, "p2")["met"] is False

    def test_list_breaches(self):
        svc = SlaTracker()
        svc.define_sla(SlaTarget("s1", "c1", "latency", 100.0, "lte"))
        svc.record("s1", 50.0, "p1")
        svc.record("s1", 150.0, "p2")
        breaches = svc.list_breaches()
        assert len(breaches) == 1
        assert breaches[0]["period"] == "p2"

    def test_undefined_sla(self):
        svc = SlaTracker()
        with pytest.raises(ValueError):
            svc.record("missing", 100.0, "p1")

    def test_isolation(self):
        a, b = SlaTracker(), SlaTracker()
        a.define_sla(SlaTarget("s1", "c1", "latency", 100.0))
        with pytest.raises(ValueError):
            b.record("s1", 50.0, "p1")
