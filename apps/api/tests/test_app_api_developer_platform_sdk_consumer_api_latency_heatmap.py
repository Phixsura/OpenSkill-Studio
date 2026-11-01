"""Tests for API Latency Heatmap service."""
import pytest
from app.services.app_api_developer_platform_sdk_consumer_api_latency_heatmap import (
    LatencyHeatmap, LatencySample,
)


class TestLatencyHeatmap:
    def test_record_and_heatmap(self):
        svc = LatencyHeatmap()
        svc.record(LatencySample("ep1", "14:00", 45.0))
        svc.record(LatencySample("ep1", "14:00", 120.0))
        svc.record(LatencySample("ep1", "15:00", 30.0))
        hm = svc.get_heatmap("ep1")
        assert len(hm["time_buckets"]) == 2
        assert hm["data"]["14:00"]["25-50ms"] == 1

    def test_percentiles(self):
        svc = LatencyHeatmap()
        for i in range(100):
            svc.record(LatencySample("ep1", "t", float(i + 1)))
        perc = svc.get_percentiles("ep1")
        assert perc["min"] == 1.0
        assert perc["max"] == 100.0
        assert perc["p90"] >= 90
        assert perc["p99"] >= 99

    def test_hot_spots(self):
        svc = LatencyHeatmap()
        for _ in range(5):
            svc.record(LatencySample("ep1", "14:00", 50.0))
        for _ in range(5):
            svc.record(LatencySample("ep1", "15:00", 800.0))
        spots = svc.get_hot_spots("ep1", threshold_ms=500)
        assert len(spots) == 1
        assert spots[0]["time_bucket"] == "15:00"

    def test_compare_endpoints(self):
        svc = LatencyHeatmap()
        for i in range(10):
            svc.record(LatencySample("fast", "t", 20.0))
            svc.record(LatencySample("slow", "t", 500.0))
        compared = svc.compare_endpoints(["fast", "slow"])
        assert compared[0]["endpoint_id"] == "fast"

    def test_empty_heatmap(self):
        svc = LatencyHeatmap()
        assert svc.get_heatmap("missing")["data"] == {}

    def test_empty_percentiles(self):
        svc = LatencyHeatmap()
        assert svc.get_percentiles("missing")["status"] == "no_data"

    def test_negative_latency_rejected(self):
        svc = LatencyHeatmap()
        with pytest.raises(ValueError):
            svc.record(LatencySample("ep1", "t", -5.0))

    def test_high_latency_bucket(self):
        svc = LatencyHeatmap()
        svc.record(LatencySample("ep1", "t", 10000.0))
        hm = svc.get_heatmap("ep1")
        assert "5000ms+" in hm["data"]["t"]

    def test_summary(self):
        svc = LatencyHeatmap()
        svc.record(LatencySample("ep1", "t", 50.0))
        svc.record(LatencySample("ep2", "t", 60.0))
        summary = svc.get_summary()
        assert summary["endpoints"] == 2
        assert summary["total_samples"] == 2

    def test_isolation(self):
        a, b = LatencyHeatmap(), LatencyHeatmap()
        a.record(LatencySample("ep1", "t", 50.0))
        assert b.get_summary()["total_samples"] == 0
