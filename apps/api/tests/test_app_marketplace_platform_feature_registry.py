from app.services.app_marketplace_platform_feature_registry import app_marketplace_platform_feature_registry_status, app_marketplace_platform_feature_registry_config, app_marketplace_platform_feature_registry_metrics, app_marketplace_platform_feature_registry_health_check

def test_status():
    r = app_marketplace_platform_feature_registry_status()
    assert r["status"] == "operational"
    assert r["healthy"]
    assert r["platform"] == "OpenSkill Developer Platform"

def test_config():
    c = app_marketplace_platform_feature_registry_config()
    assert c["enabled"]
    assert c["graceful_shutdown_timeout"] == 10

def test_metrics():
    m = app_marketplace_platform_feature_registry_metrics()
    assert m["queue_depth"] == 0

def test_health():
    h = app_marketplace_platform_feature_registry_health_check()
    assert h["all_passed"]
    assert h["response_ms"] == 1
