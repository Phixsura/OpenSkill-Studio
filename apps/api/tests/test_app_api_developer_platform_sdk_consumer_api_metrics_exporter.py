"""Tests for Consumer API Metrics Exporter service."""
import pytest
from app.services.app_api_developer_platform_sdk_consumer_api_metrics_exporter import (
    MetricsExporter, MetricDefinition,
)


class TestMetricsExporter:
    def test_define_and_record(self):
        svc = MetricsExporter()
        svc.define(MetricDefinition("http_requests_total", "counter", "Total HTTP requests"))
        svc.record("http_requests_total", 100.0)
        metric = svc.get_metric("http_requests_total")
        assert metric["total_samples"] == 1

    def test_export_prometheus(self):
        svc = MetricsExporter()
        svc.define(MetricDefinition("api_latency", "gauge", "API latency"))
        svc.record("api_latency", 42.5)
        output = svc.export_prometheus()
        assert "# HELP api_latency API latency" in output
        assert "# TYPE api_latency gauge" in output
        assert "api_latency 42.5" in output

    def test_labels(self):
        svc = MetricsExporter()
        svc.define(MetricDefinition("requests", "counter", "Reqs", ["method"]))
        svc.record("requests", 10, {"method": "GET"})
        svc.record("requests", 5, {"method": "POST"})
        output = svc.export_prometheus()
        assert 'method="GET"' in output
        assert 'method="POST"' in output

    def test_increment(self):
        svc = MetricsExporter()
        svc.define(MetricDefinition("counter", "counter", "A counter"))
        svc.increment("counter", 5)
        svc.increment("counter", 3)
        output = svc.export_prometheus()
        assert "counter 8" in output

    def test_counter_negative_rejected(self):
        svc = MetricsExporter()
        svc.define(MetricDefinition("c", "counter", ""))
        with pytest.raises(ValueError):
            svc.record("c", -1)

    def test_increment_negative_rejected(self):
        svc = MetricsExporter()
        svc.define(MetricDefinition("c", "counter", ""))
        with pytest.raises(ValueError):
            svc.increment("c", -5)

    def test_undefined_metric(self):
        svc = MetricsExporter()
        with pytest.raises(ValueError):
            svc.record("unknown", 1)

    def test_duplicate_definition(self):
        svc = MetricsExporter()
        svc.define(MetricDefinition("m", "gauge", ""))
        with pytest.raises(ValueError):
            svc.define(MetricDefinition("m", "counter", ""))

    def test_invalid_type(self):
        svc = MetricsExporter()
        with pytest.raises(ValueError):
            svc.define(MetricDefinition("m", "invalid", ""))

    def test_list_metrics(self):
        svc = MetricsExporter()
        svc.define(MetricDefinition("a", "counter", ""))
        svc.define(MetricDefinition("b", "gauge", ""))
        assert len(svc.list_metrics()) == 2

    def test_stats(self):
        svc = MetricsExporter()
        svc.define(MetricDefinition("c1", "counter", ""))
        svc.define(MetricDefinition("g1", "gauge", ""))
        svc.record("c1", 1)
        svc.record("g1", 5)
        stats = svc.get_stats()
        assert stats["total_metrics"] == 2
        assert stats["total_samples"] == 2

    def test_isolation(self):
        a, b = MetricsExporter(), MetricsExporter()
        a.define(MetricDefinition("m", "gauge", ""))
        assert b.get_metric("m") is None
