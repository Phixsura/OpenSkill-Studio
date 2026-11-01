from app.services.app_marketplace_extension_sandbox_metrics_collector import (
    SandboxMetricsCollectorService,
)


def test_record_and_query():
    svc = SandboxMetricsCollectorService()
    svc.record("sb-1", "cpu_percent", 45.5)
    svc.record("sb-1", "cpu_percent", 55.0)
    points = svc.query("sb-1", "cpu_percent", last_seconds=60)
    assert len(points) == 2


def test_aggregate():
    svc = SandboxMetricsCollectorService()
    for v in [10, 20, 30, 40, 50]:
        svc.record("sb-1", "latency_ms", v)
    agg = svc.aggregate("sb-1", "latency_ms")
    assert agg["count"] == 5
    assert agg["avg"] == 30.0
    assert agg["min"] == 10
    assert agg["max"] == 50


def test_list_metrics():
    svc = SandboxMetricsCollectorService()
    svc.record("sb-1", "cpu", 50)
    svc.record("sb-1", "memory", 70)
    svc.record("sb-1", "cpu", 60)
    names = svc.list_metric_names("sb-1")
    assert names == ["cpu", "memory"]


def test_get_current():
    svc = SandboxMetricsCollectorService()
    svc.record("sb-1", "cpu", 50)
    svc.record("sb-1", "cpu", 75)
    svc.record("sb-1", "memory", 80)
    current = svc.get_current("sb-1")
    assert current["cpu"] == 75  # latest
    assert current["memory"] == 80


def test_threshold_check():
    svc = SandboxMetricsCollectorService()
    svc.record("sb-1", "cpu", 95)
    result = svc.check_threshold("sb-1", "cpu", 90)
    assert result["exceeded"] is True
    assert result["current"] == 95


def test_threshold_not_exceeded():
    svc = SandboxMetricsCollectorService()
    svc.record("sb-1", "cpu", 50)
    result = svc.check_threshold("sb-1", "cpu", 90)
    assert result["exceeded"] is False


def test_tags():
    svc = SandboxMetricsCollectorService()
    svc.record("sb-1", "requests", 100, tags={"endpoint": "/api/data"})
    points = svc.query("sb-1", "requests")
    assert points[0].tags["endpoint"] == "/api/data"


def test_empty_aggregate():
    svc = SandboxMetricsCollectorService()
    agg = svc.aggregate("sb-x", "nonexistent")
    assert agg["count"] == 0
