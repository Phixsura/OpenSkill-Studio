from app.services.app_marketplace_extension_metrics_exporter import (
    MetricsExporterService, MetricType,
)
import pytest


def test_counter():
    svc = MetricsExporterService()
    svc.register("http_requests_total", MetricType.COUNTER, "Total HTTP requests")
    svc.inc("http_requests_total")
    svc.inc("http_requests_total", 5)
    assert svc.get_counter("http_requests_total") == 6.0


def test_counter_no_negative():
    svc = MetricsExporterService()
    svc.register("c", MetricType.COUNTER)
    with pytest.raises(ValueError, match="increase"):
        svc.inc("c", -1)


def test_gauge():
    svc = MetricsExporterService()
    svc.register("cpu_usage", MetricType.GAUGE, "CPU usage percent")
    svc.set_gauge("cpu_usage", 42.5)
    assert svc.get_gauge("cpu_usage") == 42.5
    svc.set_gauge("cpu_usage", 30.0)
    assert svc.get_gauge("cpu_usage") == 30.0


def test_histogram():
    svc = MetricsExporterService()
    svc.register("request_duration", MetricType.HISTOGRAM)
    for v in [10, 20, 30, 40, 50]:
        svc.observe("request_duration", v)
    stats = svc.get_histogram_stats("request_duration")
    assert stats["count"] == 5
    assert stats["avg"] == 30.0
    assert stats["p50"] == 30


def test_labels():
    svc = MetricsExporterService()
    svc.register("requests", MetricType.COUNTER)
    svc.inc("requests", labels={"method": "GET"})
    svc.inc("requests", labels={"method": "POST"})
    svc.inc("requests", labels={"method": "GET"})
    assert svc.get_counter("requests", {"method": "GET"}) == 2.0
    assert svc.get_counter("requests", {"method": "POST"}) == 1.0


def test_export_text():
    svc = MetricsExporterService()
    svc.register("up", MetricType.GAUGE, "Service status")
    svc.set_gauge("up", 1)
    text = svc.export_text()
    assert "# HELP up Service status" in text
    assert "# TYPE up gauge" in text
    assert "up 1" in text


def test_invalid_name():
    svc = MetricsExporterService()
    with pytest.raises(ValueError, match="Invalid"):
        svc.register("bad metric!", MetricType.COUNTER)
