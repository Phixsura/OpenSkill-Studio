from app.services.app_marketplace_app_app_app_app_app_app_app_ep_maturity import assess_maturity

def test_mature():
    r = assess_maturity({"path": "/api/users", "has_docs": True, "has_tests": True,
                          "has_monitoring": True, "has_error_handling": True,
                          "has_rate_limit": True, "has_versioning": True,
                          "has_auth": True, "has_caching": True})
    assert r["level"] == "mature"
    assert r["pct"] == 100

def test_initial():
    r = assess_maturity({"path": "/api/legacy", "has_docs": False, "has_tests": True})
    assert r["level"] == "initial"
    assert r["score"] == 1
