"""Tests for Consumer API Health Report service."""
import pytest
from app.services.app_api_developer_platform_sdk_consumer_api_health_report import (
    HealthReportGenerator, HealthMetric,
)


class TestHealthReportGenerator:
    def test_generate_healthy(self):
        svc = HealthReportGenerator()
        metrics = [
            HealthMetric("latency_p95", 80, 200),
            HealthMetric("error_rate", 0.5, 5),
        ]
        result = svc.generate("r1", "c1", "2024-10", metrics)
        assert result["overall_score"] == 100.0
        assert result["grade"] == "A"
        assert result["recommendations"] == 0

    def test_generate_with_warnings(self):
        svc = HealthReportGenerator()
        metrics = [
            HealthMetric("latency_p95", 250, 200),  # warning
            HealthMetric("error_rate", 0.5, 5),  # healthy
        ]
        result = svc.generate("r1", "c1", "2024-10", metrics)
        assert result["overall_score"] == 80.0
        assert result["recommendations"] == 1

    def test_generate_critical(self):
        svc = HealthReportGenerator()
        metrics = [
            HealthMetric("latency_p95", 500, 200),  # critical
            HealthMetric("error_rate", 15, 5),  # critical
        ]
        result = svc.generate("r1", "c1", "2024-10", metrics)
        assert result["overall_score"] == 20.0
        assert result["grade"] == "F"

    def test_get_report(self):
        svc = HealthReportGenerator()
        svc.generate("r1", "c1", "2024-10", [HealthMetric("latency", 50, 200)])
        report = svc.get_report("r1")
        assert report is not None
        assert report["period"] == "2024-10"
        assert len(report["metrics"]) == 1

    def test_compare_reports(self):
        svc = HealthReportGenerator()
        svc.generate("r1", "c1", "2024-09", [HealthMetric("x", 50, 200)])
        svc.generate("r2", "c1", "2024-10", [HealthMetric("x", 250, 200)])
        diff = svc.compare("r1", "r2")
        assert diff["trend"] == "declining"
        assert diff["change"] < 0

    def test_list_reports(self):
        svc = HealthReportGenerator()
        svc.generate("r1", "c1", "2024-09", [HealthMetric("x", 50, 200)])
        svc.generate("r2", "c2", "2024-10", [HealthMetric("x", 50, 200)])
        assert len(svc.list_reports(consumer_id="c1")) == 1

    def test_stats(self):
        svc = HealthReportGenerator()
        svc.generate("r1", "c1", "p1", [HealthMetric("x", 50, 200)])
        svc.generate("r2", "c1", "p2", [HealthMetric("x", 400, 200)])
        stats = svc.get_stats()
        assert stats["total_reports"] == 2
        assert stats["best_score"] == 100.0

    def test_empty_metrics(self):
        svc = HealthReportGenerator()
        with pytest.raises(ValueError):
            svc.generate("r1", "c1", "p1", [])

    def test_duplicate_report(self):
        svc = HealthReportGenerator()
        svc.generate("r1", "c1", "p1", [HealthMetric("x", 50, 200)])
        with pytest.raises(ValueError):
            svc.generate("r1", "c1", "p2", [HealthMetric("x", 50, 200)])

    def test_isolation(self):
        a, b = HealthReportGenerator(), HealthReportGenerator()
        a.generate("r1", "c1", "p1", [HealthMetric("x", 50, 200)])
        assert b.get_report("r1") is None
