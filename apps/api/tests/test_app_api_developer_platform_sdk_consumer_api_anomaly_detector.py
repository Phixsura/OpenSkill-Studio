"""Tests for Consumer API Anomaly Detector service."""
import pytest
from app.services.app_api_developer_platform_sdk_consumer_api_anomaly_detector import (
    AnomalyDetector, MetricSample,
)


class TestAnomalyDetector:
    def _seed(self, svc, metric="latency", values=None):
        for v in (values or [50, 52, 48, 51, 49, 50, 53, 47, 50, 51]):
            svc.record(MetricSample(metric, v))

    def test_detect_spike(self):
        svc = AnomalyDetector()
        self._seed(svc)
        result = svc.detect("latency", 200.0)
        assert result["anomaly"] is True
        assert result["type"] == "spike"

    def test_detect_dip(self):
        svc = AnomalyDetector()
        self._seed(svc, values=[100, 102, 98, 101, 99, 100, 103, 97, 100, 101])
        result = svc.detect("latency", 10.0)
        assert result["anomaly"] is True
        assert result["type"] == "dip"

    def test_normal_value(self):
        svc = AnomalyDetector()
        self._seed(svc)
        result = svc.detect("latency", 51.0)
        assert result["anomaly"] is False

    def test_insufficient_data(self):
        svc = AnomalyDetector()
        svc.record(MetricSample("x", 10))
        result = svc.detect("x", 100)
        assert result["reason"] == "insufficient_data"

    def test_custom_threshold(self):
        svc = AnomalyDetector()
        svc.configure_threshold("latency", 1.0)
        self._seed(svc)
        result = svc.detect("latency", 60.0)  # mild deviation
        assert result["anomaly"] is True

    def test_get_anomalies(self):
        svc = AnomalyDetector()
        self._seed(svc)
        svc.detect("latency", 200.0)
        svc.detect("latency", 300.0)
        anomalies = svc.get_anomalies()
        assert len(anomalies) >= 1

    def test_get_baseline(self):
        svc = AnomalyDetector()
        self._seed(svc)
        baseline = svc.get_baseline("latency")
        assert baseline["sample_count"] == 10
        assert 45 < baseline["mean"] < 55

    def test_baseline_insufficient(self):
        svc = AnomalyDetector()
        svc.record(MetricSample("x", 10))
        assert svc.get_baseline("x")["status"] == "insufficient_data"

    def test_stats(self):
        svc = AnomalyDetector()
        self._seed(svc)
        svc.detect("latency", 200.0)
        stats = svc.get_stats()
        assert stats["metrics_tracked"] == 1
        assert stats["total_anomalies"] >= 1

    def test_invalid_threshold(self):
        svc = AnomalyDetector()
        with pytest.raises(ValueError):
            svc.configure_threshold("x", 0)

    def test_isolation(self):
        a, b = AnomalyDetector(), AnomalyDetector()
        a.record(MetricSample("x", 50))
        assert b.get_stats()["metrics_tracked"] == 0
