from app.services.app_marketplace_platform_cache_layer import app_marketplace_platform_cache_layer_status, app_marketplace_platform_cache_layer_config

def test_status():
    r = app_marketplace_platform_cache_layer_status()
    assert r["status"] == "operational"
    assert r["healthy"]

def test_config():
    c = app_marketplace_platform_cache_layer_config()
    assert c["enabled"]
    assert c["timeout_ms"] == 5000
