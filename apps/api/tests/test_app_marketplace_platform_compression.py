from app.services.app_marketplace_platform_compression import app_marketplace_platform_compression_status, app_marketplace_platform_compression_config, app_marketplace_platform_compression_metrics

def test_status():
    r = app_marketplace_platform_compression_status()
    assert r["status"] == "operational"
    assert r["healthy"]
    assert r["uptime_pct"] == 99.99

def test_config():
    c = app_marketplace_platform_compression_config()
    assert c["enabled"]
    assert c["metrics_enabled"]

def test_metrics():
    m = app_marketplace_platform_compression_metrics()
    assert m["service"] == "app_marketplace_platform_compression"
