from app.services.app_marketplace_extension_sandbox_network_monitor import (
    SandboxNetworkMonitorService, RequestMethod,
)


def test_record_and_summary():
    svc = SandboxNetworkMonitorService()
    svc.record("sb-1", RequestMethod.GET, "https://api.example.com/data",
               200, request_bytes=100, response_bytes=5000, latency_ms=45)
    summary = svc.get_summary("sb-1")
    assert summary["total_requests"] == 1
    assert summary["by_method"]["GET"] == 1


def test_bandwidth():
    svc = SandboxNetworkMonitorService()
    svc.record("sb-1", RequestMethod.GET, "https://a.com", 200,
               request_bytes=1024, response_bytes=1048576)
    bw = svc.get_bandwidth("sb-1")
    assert bw["total_mb"] > 0
    assert bw["limit_mb"] == 100


def test_latency_stats():
    svc = SandboxNetworkMonitorService()
    for ms in [10, 20, 30, 40, 50, 60, 70, 80, 90, 100]:
        svc.record("sb-1", RequestMethod.GET, "https://a.com", 200, latency_ms=ms)
    stats = svc.get_latency_stats("sb-1")
    assert stats["count"] == 10
    assert stats["avg"] == 55.0
    assert stats["p50"] == 60


def test_top_endpoints():
    svc = SandboxNetworkMonitorService()
    for _ in range(5):
        svc.record("sb-1", RequestMethod.GET, "https://a.com/api", 200)
    for _ in range(3):
        svc.record("sb-1", RequestMethod.POST, "https://b.com/data", 200)
    top = svc.get_top_endpoints("sb-1", 2)
    assert top[0]["url"] == "https://a.com/api"
    assert top[0]["count"] == 5


def test_error_rate():
    svc = SandboxNetworkMonitorService()
    for _ in range(7):
        svc.record("sb-1", RequestMethod.GET, "https://a.com", 200)
    for _ in range(3):
        svc.record("sb-1", RequestMethod.GET, "https://a.com", 500)
    assert svc.get_error_rate("sb-1") == 30.0


def test_anomaly_detection():
    svc = SandboxNetworkMonitorService()
    # High error rate
    for _ in range(3):
        svc.record("sb-1", RequestMethod.GET, "https://a.com", 200)
    for _ in range(7):
        svc.record("sb-1", RequestMethod.GET, "https://a.com", 500)
    anomalies = svc.detect_anomalies("sb-1")
    assert any("error rate" in a.lower() for a in anomalies)


def test_empty_sandbox():
    svc = SandboxNetworkMonitorService()
    assert svc.get_error_rate("sb-x") == 0.0
    assert svc.get_latency_stats("sb-x")["count"] == 0
