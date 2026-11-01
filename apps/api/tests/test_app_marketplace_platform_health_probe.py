from app.services.app_marketplace_platform_health_probe import app_marketplace_platform_health_probe_status, app_marketplace_platform_health_probe_config

def test_status():
    r = app_marketplace_platform_health_probe_status()
    assert r["status"] == "operational"
    assert r["healthy"]

def test_config():
    c = app_marketplace_platform_health_probe_config()
    assert c["enabled"]
    assert c["timeout_ms"] == 5000
