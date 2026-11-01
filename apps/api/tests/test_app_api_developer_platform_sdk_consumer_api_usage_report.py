"""Tests for Consumer API Usage Report service."""
import pytest
from app.services.app_api_developer_platform_sdk_consumer_api_usage_report import (
    UsageReportGenerator, UsageEntry,
)


class TestUsageReportGenerator:
    def test_record_and_generate(self):
        svc = UsageReportGenerator()
        svc.record("c1", UsageEntry("ep1", "2024-01", 500, 10, 45.0, 50000))
        svc.record("c1", UsageEntry("ep2", "2024-01", 200, 5, 80.0, 20000))
        result = svc.generate("r1", "c1", "2024-01", "2024-01")
        assert result["endpoints"] == 2
        assert result["total_requests"] == 700

    def test_aggregation(self):
        svc = UsageReportGenerator()
        svc.record("c1", UsageEntry("ep1", "2024-01", 100, 5, 40.0))
        svc.record("c1", UsageEntry("ep1", "2024-01", 200, 10, 60.0))
        svc.generate("r1", "c1", "2024-01", "2024-01")
        report = svc.get_report("r1")
        assert report["total_requests"] == 300
        assert report["total_errors"] == 15

    def test_period_filter(self):
        svc = UsageReportGenerator()
        svc.record("c1", UsageEntry("ep1", "2024-01", 100))
        svc.record("c1", UsageEntry("ep1", "2024-02", 200))
        svc.record("c1", UsageEntry("ep1", "2024-03", 300))
        svc.generate("r1", "c1", "2024-01", "2024-02")
        report = svc.get_report("r1")
        assert report["total_requests"] == 300  # jan + feb only

    def test_finalize(self):
        svc = UsageReportGenerator()
        svc.record("c1", UsageEntry("ep1", "2024-01", 100))
        svc.generate("r1", "c1", "2024-01", "2024-01")
        svc.finalize("r1")
        assert svc.get_report("r1")["status"] == "finalized"

    def test_export_csv(self):
        svc = UsageReportGenerator()
        svc.record("c1", UsageEntry("ep1", "2024-01", 100, 5, 40.0, 1000))
        svc.generate("r1", "c1", "2024-01", "2024-01")
        csv = svc.export_csv("r1")
        assert "endpoint_id,requests" in csv
        assert "ep1,100,5" in csv

    def test_error_rate(self):
        svc = UsageReportGenerator()
        svc.record("c1", UsageEntry("ep1", "2024-01", 100, 20))
        svc.generate("r1", "c1", "2024-01", "2024-01")
        report = svc.get_report("r1")
        assert report["error_rate"] == 20.0

    def test_list_reports(self):
        svc = UsageReportGenerator()
        svc.record("c1", UsageEntry("ep1", "2024-01", 100))
        svc.record("c2", UsageEntry("ep1", "2024-01", 200))
        svc.generate("r1", "c1", "2024-01", "2024-01")
        svc.generate("r2", "c2", "2024-01", "2024-01")
        assert len(svc.list_reports(consumer_id="c1")) == 1

    def test_duplicate_report(self):
        svc = UsageReportGenerator()
        svc.record("c1", UsageEntry("ep1", "2024-01", 100))
        svc.generate("r1", "c1", "2024-01", "2024-01")
        with pytest.raises(ValueError):
            svc.generate("r1", "c1", "2024-01", "2024-01")

    def test_not_found(self):
        svc = UsageReportGenerator()
        assert svc.get_report("missing") is None

    def test_isolation(self):
        a, b = UsageReportGenerator(), UsageReportGenerator()
        a.record("c1", UsageEntry("ep1", "2024-01", 100))
        a.generate("r1", "c1", "2024-01", "2024-01")
        assert b.get_report("r1") is None
