from app.services.app_marketplace_app_health_endpoint import health_check
def test_health():
    r = health_check()
    assert r["status"] == "ok"
