from app.services.app_marketplace_platform_prometheus import get_prometheus
def test_prometheus():
    r = get_prometheus()
    assert r["flames_kindled"] > 4000
    assert r["chains"] == "BROKEN — Prometheus is free"
    assert r["gift"]["duration"] == "ETERNAL"
    assert r["eagle"].startswith("DEFEATED")
    assert "NEVER STOPS" in r["status"]
