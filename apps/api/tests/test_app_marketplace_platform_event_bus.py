from app.services.app_marketplace_platform_event_bus import app_marketplace_platform_event_bus_status, app_marketplace_platform_event_bus_config

def test_status():
    r = app_marketplace_platform_event_bus_status()
    assert r["status"] == "operational"
    assert r["healthy"]

def test_config():
    c = app_marketplace_platform_event_bus_config()
    assert c["enabled"]
    assert c["timeout_ms"] == 5000
