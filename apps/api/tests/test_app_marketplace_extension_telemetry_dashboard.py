from app.services.app_marketplace_extension_telemetry_dashboard import TelemetryDashboardService


def test_update_and_snapshot():
    svc = TelemetryDashboardService()
    svc.update("ext-1", request_count=10000, error_count=50,
               avg_latency_ms=45, p99_latency_ms=200, cpu_percent=60)
    snap = svc.get_snapshot("ext-1")
    assert snap["metrics"]["requests"] == 10000
    assert snap["metrics"]["error_rate"] == 0.5
    assert snap["resources"]["cpu"] == 60


def test_health_score_good():
    svc = TelemetryDashboardService()
    svc.update("ext-1", request_count=10000, error_count=10,
               p99_latency_ms=100, cpu_percent=30)
    snap = svc.get_snapshot("ext-1")
    assert snap["health"]["score"] >= 90


def test_health_score_bad():
    svc = TelemetryDashboardService()
    svc.update("ext-1", request_count=100, error_count=20,
               p99_latency_ms=6000, cpu_percent=95, log_error_count=100,
               active_alerts=3)
    snap = svc.get_snapshot("ext-1")
    assert snap["health"]["score"] < 50


def test_all_health():
    svc = TelemetryDashboardService()
    svc.update("ext-healthy", request_count=1000, error_count=1)
    svc.update("ext-sick", request_count=100, error_count=50, cpu_percent=95)
    health = svc.get_all_health()
    assert health[0]["extension_id"] == "ext-sick"  # worst first
