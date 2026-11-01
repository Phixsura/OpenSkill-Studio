"""Tests for Throughput Analyzer service."""
import pytest
from app.services.app_api_developer_platform_sdk_consumer_api_throughput_analyzer import (
    ThroughputAnalyzer,
    ThroughputSample,
)


class TestThroughputAnalyzer:
    def test_record_and_analyze(self):
        svc = ThroughputAnalyzer()
        svc.record(ThroughputSample("ep1", "2024-01-01T00:00:00Z", 100.0, 50.0, 2))
        svc.record(ThroughputSample("ep1", "2024-01-01T00:01:00Z", 150.0, 60.0, 1))
        result = svc.analyze("ep1")
        assert result["sample_count"] == 2
        assert result["peak_rps"] == 150.0
        assert result["avg_rps"] == 125.0
        assert result["avg_latency_ms"] == 55.0
        assert result["total_errors"] == 3
        assert result["capacity_status"] == "healthy"

    def test_overloaded_status(self):
        svc = ThroughputAnalyzer()
        svc.record(ThroughputSample("ep1", "t1", 50.0, 600.0))
        result = svc.analyze("ep1")
        assert result["capacity_status"] == "overloaded"

    def test_stressed_status(self):
        svc = ThroughputAnalyzer()
        svc.record(ThroughputSample("ep1", "t1", 50.0, 300.0))
        result = svc.analyze("ep1")
        assert result["capacity_status"] == "stressed"

    def test_spiky_status(self):
        svc = ThroughputAnalyzer()
        svc.record(ThroughputSample("ep1", "t1", 10.0, 50.0))
        svc.record(ThroughputSample("ep1", "t2", 10.0, 50.0))
        svc.record(ThroughputSample("ep1", "t3", 100.0, 50.0))
        result = svc.analyze("ep1")
        assert result["capacity_status"] == "spiky"

    def test_forecast(self):
        svc = ThroughputAnalyzer()
        svc.record(ThroughputSample("ep1", "t1", 100.0, 50.0))
        forecast = svc.forecast("ep1", growth_rate=0.5)
        assert forecast["current_avg_rps"] == 100.0
        assert forecast["estimated_capacity_rps"] == 200.0
        assert forecast["periods_to_capacity"] > 0

    def test_forecast_no_data(self):
        svc = ThroughputAnalyzer()
        result = svc.forecast("none")
        assert result["forecast"] == "insufficient_data"

    def test_compare(self):
        svc = ThroughputAnalyzer()
        svc.record(ThroughputSample("ep1", "t1", 50.0, 30.0))
        svc.record(ThroughputSample("ep2", "t1", 200.0, 20.0))
        ranked = svc.compare(["ep1", "ep2"])
        assert ranked[0]["endpoint_id"] == "ep2"
        assert ranked[0]["rank"] == 1
        assert ranked[1]["rank"] == 2

    def test_negative_rps_rejected(self):
        svc = ThroughputAnalyzer()
        with pytest.raises(ValueError):
            svc.record(ThroughputSample("ep1", "t1", -10.0, 50.0))

    def test_no_data_analysis(self):
        svc = ThroughputAnalyzer()
        assert svc.analyze("missing")["status"] == "no_data"

    def test_isolation(self):
        a, b = ThroughputAnalyzer(), ThroughputAnalyzer()
        a.record(ThroughputSample("ep1", "t1", 100.0, 50.0))
        assert b.analyze("ep1")["status"] == "no_data"
