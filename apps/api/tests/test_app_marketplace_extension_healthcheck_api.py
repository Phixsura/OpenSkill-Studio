from app.services.app_marketplace_extension_healthcheck_api import PlatformHealthCheckApiService


def test_healthy():
    svc = PlatformHealthCheckApiService()
    svc.register_component("api", "healthy", 5)
    svc.register_component("db", "healthy", 10)
    result = svc.check()
    assert result["status"] == "healthy"
    assert svc.is_healthy() is True
    assert result["version"] == "4.0.0"


def test_degraded():
    svc = PlatformHealthCheckApiService()
    svc.register_component("api", "healthy")
    svc.register_component("cache", "degraded", message="High latency")
    result = svc.check()
    assert result["status"] == "degraded"
    assert svc.is_ready() is True


def test_down():
    svc = PlatformHealthCheckApiService()
    svc.register_component("api", "healthy")
    svc.register_component("db", "down", message="Connection refused")
    result = svc.check()
    assert result["status"] == "down"
    assert svc.is_healthy() is False
    assert svc.is_ready() is False


def test_uptime():
    svc = PlatformHealthCheckApiService()
    result = svc.check()
    assert result["uptime_seconds"] >= 0
    assert result["timestamp"] > 0
