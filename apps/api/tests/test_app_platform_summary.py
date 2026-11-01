"""Platform summary tests."""
from app.services.app_platform_summary import compute_platform_summary

def test_healthy():
    s = compute_platform_summary(total_developers=10, total_apps=50, published_apps=30,
        total_installations=200, total_executions_24h=1000, error_rate_24h=1.5)
    assert s["health"] == "healthy"
    assert s["apps"]["published"] == 30

def test_degraded():
    s = compute_platform_summary(error_rate_24h=10.0)
    assert s["health"] == "degraded"

def test_critical():
    s = compute_platform_summary(error_rate_24h=20.0)
    assert s["health"] == "critical"

def test_empty():
    s = compute_platform_summary()
    assert s["developers"] == 0
    assert s["health"] == "healthy"
