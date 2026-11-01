from app.services.app_marketplace_app_app_app_app_app_app_app_cors_manager import CorsManager

def test_cors():
    mgr = CorsManager()
    mgr.add_origin("https://app.example.com")
    mgr.add_origin("https://staging.example.com")
    r = mgr.check_origin("https://app.example.com")
    assert r["allowed"]
    assert "GET" in r["methods"]
    r2 = mgr.check_origin("https://evil.com")
    assert not r2["allowed"]
    p = mgr.policy()
    assert len(p["origins"]) == 2
    assert p["credentials"]

def test_invalid():
    mgr = CorsManager()
    r = mgr.add_origin("not-a-url")
    assert "error" in r
