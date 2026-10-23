from app.services.app_marketplace_platform_health_api import get_platform_health

def test_health():
    r = get_platform_health()
    assert r["all_healthy"]
    assert r["checks"]["database"] == "ok"
